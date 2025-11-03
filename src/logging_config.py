import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        "simple": {"format": "[%(levelname)s] %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple", "level": "INFO"},
        "app_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{LOG_DIR}/app.log",
            "formatter": "detailed",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
        "db_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{LOG_DIR}/db.log",
            "formatter": "detailed",
            "maxBytes": 10485760,
            "backupCount": 5,
        },
    },
    "loggers": {
        "": {"handlers": ["console", "app_file"], "level": "INFO"},  # Root logger
        "dao.mongo_manager_dao": {  # Todos los DAOs
            "handlers": ["db_file"],
            "level": "INFO",
            "propagate": False,
        },
        "services.rss_service": {
            "handlers": ["console", "app_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
