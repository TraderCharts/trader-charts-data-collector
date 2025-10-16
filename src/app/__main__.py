from config import DOWNLOAD_DIR, MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION
from clients.selenium_client import SeleniumClient
from dao.mongo_manager_dao import MongoManagerDAO
from dao.file_manager_dao import FileManagerDAO
from services.download_service import DownloadService

def main():
    selenium_client = SeleniumClient(DOWNLOAD_DIR)
    file_manager = FileManagerDAO(DOWNLOAD_DIR)
    mongo_manager = MongoManagerDAO(MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION)
    service = DownloadService(selenium_client, file_manager, mongo_manager)

    urls = [
        ("https://www.rava.com/perfil/DOLAR%20MEP", "Dolar MEP")
    ]
    service.download_and_store(urls)

    selenium_client.quit()

if __name__ == "__main__":
    main()
