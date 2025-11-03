import logging
import os

from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

from config import MONGO_DB_NAME, MONGO_URI
from dao.mongo_manager_dao import MongoManagerDAO

logger = logging.getLogger(__name__)


class ModelTester:
    def __init__(self, mongo_manager_dao):
        self.mongo_manager = mongo_manager_dao
        self.models_base_path = "./llm_models"

    def _get_fine_tuned_models(self):
        """Obtiene modelos fine-tuned desde MongoDB"""
        fine_tuned_models = self.mongo_manager.db.sentiment_model_metadata.find({"is_base_model": False}).sort("created_at", -1)  # Los más recientes primero

        model_list = []
        for model in fine_tuned_models:
            # Tomar solo los más recientes de cada base_model (último fine-tuning)
            base_model = model["fine_tuned_from"]
            if not any(m["fine_tuned_from"] == base_model for m in model_list):
                model_list.append(
                    {
                        "model_id": model["model_id"],
                        "model_name": model["model_name"],
                        "base_model": model["base_model"],
                        "model_path": model["model_path"],
                        "fine_tuned_from": model["fine_tuned_from"],
                        "previous_accuracy": model.get("performance_metrics", {}).get("accuracy", 0),
                    }
                )

        if not model_list:
            raise ValueError("❌ No hay modelos fine-tuned en sentiment_model_metadata")

        return model_list

    def _get_final_test_data(self):
        """Obtiene datos frescos de test final"""
        test_data = list(self.mongo_manager.db.sentiment_final_test.find({}, {"_id": 0}))

        if not test_data:
            raise ValueError("❌ No hay datos de test final en sentiment_final_test")

        print(f"📊 Datos de test final (frescos): {len(test_data)} ejemplos")

        # Mostrar distribución de labels
        from collections import Counter

        label_counts = Counter(item["label"] for item in test_data)
        print(f"📈 Distribución de labels: {dict(label_counts)}")

        return test_data

    def _load_model(self, model_info):
        """Carga un modelo fine-tuned"""
        model_path = model_info["model_path"]
        if not os.path.exists(model_path):
            raise ValueError(f"❌ Modelo no encontrado en: {model_path}")

        print(f"🔧 Cargando modelo: {model_info['model_name']}")
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)

        return model, tokenizer

    def evaluate_model(self, model, tokenizer, test_data, model_name):
        """Evalúa un modelo con datos frescos mostrando probabilidades completas"""
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=model,
            tokenizer=tokenizer,
            return_all_scores=True,  # 🔥 DEVUELVE TODAS LAS PROBABILIDADES
            device=0 if torch.backends.mps.is_built() else -1,
        )

        correct = 0
        results = []

        print(f"🧪 Evaluando {model_name}...")

        for i, test_item in enumerate(test_data):
            try:
                # 🔥 AHORA DEVUELVE TODAS LAS SCORES
                result = sentiment_pipeline(test_item["text"][:512])[0]

                # Encontrar la predicción con mayor probabilidad
                best_pred = max(result, key=lambda x: x["score"])
                predicted = best_pred["label"]
                confidence = best_pred["score"]

                is_correct = predicted == test_item["label"]

                # 🔥 MOSTRAR PROBABILIDADES COMPLETAS PARA ERRORES
                if not is_correct:
                    print(f"   ❌ ERROR #{i + 1}")
                    print(f"      Texto: '{test_item['text'][:60]}...'")
                    print(f"      Esperado: {test_item['label']}")
                    print(f"      Predicción: {predicted} ({confidence:.1%})")
                    print("      🔍 Probabilidades completas:")
                    for score in sorted(result, key=lambda x: x["score"], reverse=True):
                        marker = "←" if score["label"] == predicted else ""
                        print(f"         {score['label']}: {score['score']:.3f} ({score['score']:.1%}) {marker}")
                    print()

                if is_correct:
                    correct += 1

                results.append(
                    {
                        "text": test_item["text"],
                        "expected": test_item["label"],
                        "predicted": predicted,
                        "confidence": confidence,
                        "all_scores": result,  # 🔥 GUARDAR TODAS LAS PROBABILIDADES
                        "correct": is_correct,
                    }
                )

            except Exception as e:
                print(f"❌ Error procesando ejemplo {i}: {e}")
                continue

        accuracy = correct / len(test_data)

        # Calcular métricas por label
        from collections import defaultdict

        label_metrics = defaultdict(lambda: {"correct": 0, "total": 0})

        for result in results:
            label = result["expected"]
            label_metrics[label]["total"] += 1
            if result["correct"]:
                label_metrics[label]["correct"] += 1

        print(f"📊 {model_name} - Accuracy: {accuracy:.1%}")
        for label, metrics in label_metrics.items():
            label_accuracy = metrics["correct"] / metrics["total"] if metrics["total"] > 0 else 0
            print(f"   • {label}: {metrics['correct']}/{metrics['total']} ({label_accuracy:.1%})")

        return accuracy, results

    def run_final_evaluation(self):
        """Ejecuta evaluación final con datos frescos para todos los modelos fine-tuned"""
        print("🎯 EVALUACIÓN FINAL CON DATOS FRESCOS")
        print("=" * 50)

        # Obtener modelos fine-tuned
        fine_tuned_models = self._get_fine_tuned_models()
        print(f"📋 MODELOS FINE-TUNED ENCONTRADOS ({len(fine_tuned_models)}):")
        for model in fine_tuned_models:
            print(f"   • {model['model_name']} (prev: {model['previous_accuracy']:.1%})")

        # Obtener datos frescos
        test_data = self._get_final_test_data()

        evaluation_results = []

        for model_info in fine_tuned_models:
            print(f"\n🔍 EVALUANDO: {model_info['model_name']}")
            print("-" * 40)

            try:
                # Cargar modelo
                model, tokenizer = self._load_model(model_info)

                # Evaluar
                accuracy, results = self.evaluate_model(model, tokenizer, test_data, model_info["model_name"])

                evaluation_results.append({"model_info": model_info, "accuracy": accuracy, "results": results})

                # Mostrar algunos ejemplos
                print("\n🔎 MUESTRA DE RESULTADOS:")
                correct_examples = [r for r in results if r["correct"]]
                incorrect_examples = [r for r in results if not r["correct"]]

                if incorrect_examples:
                    print("   ❌ EJEMPLOS INCORRECTOS:")
                    for i, example in enumerate(incorrect_examples[:3]):
                        print(f"      {i + 1}. '{example['text'][:50]}...'")
                        print(f"         → Esperado: {example['expected']}, Predicho: {example['predicted']} ({example['confidence']:.1%})")

                if correct_examples:
                    print("   ✅ EJEMPLOS CORRECTOS:")
                    for i, example in enumerate(correct_examples[:2]):
                        print(f"      {i + 1}. '{example['text'][:50]}...'")
                        print(f"         → {example['predicted']} ({example['confidence']:.1%})")

            except Exception as e:
                print(f"❌ Error evaluando {model_info['model_name']}: {e}")
                continue

        if not evaluation_results:
            raise Exception("❌ Ningún modelo pudo ser evaluado exitosamente")

        # Seleccionar mejor modelo
        best_result = max(evaluation_results, key=lambda x: x["accuracy"])
        best_model = best_result["model_info"]

        print("\n🏆 MEJOR MODELO SELECCIONADO:")
        print(f"   📛 {best_model['model_name']}")
        print(f"   📊 Accuracy final: {best_result['accuracy']:.1%}")
        print(f"   🔧 Base: {best_model['fine_tuned_from']}")

        # Comparar con accuracy anterior
        improvement = best_result["accuracy"] - best_model["previous_accuracy"]
        print(f"   📈 Mejora vs test anterior: {improvement:+.1%}")

        return {
            "best_model": best_model,
            "best_accuracy": best_result["accuracy"],
            "all_results": evaluation_results,
        }


def main():
    """MAIN PARA EVALUACIÓN FINAL DE MODELOS"""
    print("🚀 INICIANDO EVALUACIÓN FINAL CON DATOS FRESCOS")
    print("=" * 50)

    # Configuración MongoDB
    mongo_manager = MongoManagerDAO(MONGO_URI, MONGO_DB_NAME, "sentiment_collections")

    # Importar torch para device detection
    global torch
    import torch

    # Ejecutar evaluación
    tester = ModelTester(mongo_manager)
    results = tester.run_final_evaluation()

    print("\n🎉 EVALUACIÓN COMPLETADA")
    print(f"🏆 Mejor modelo: {results['best_model']['model_name']}")
    print(f"📊 Accuracy final: {results['best_accuracy']:.1%}")


if __name__ == "__main__":
    main()
