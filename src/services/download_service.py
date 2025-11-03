from clients.selenium_client import SeleniumClient
from dao.file_manager_dao import FileManagerDAO
from dao.mongo_manager_dao import MongoManagerDAO


class DownloadService:
    def __init__(
        self,
        selenium_client: SeleniumClient,
        file_manager: FileManagerDAO,
        mongo_manager: MongoManagerDAO,
    ):
        self.selenium_client = selenium_client
        self.file_manager = file_manager
        self.mongo_manager = mongo_manager

    def download_and_store(self, urls: list):
        for url, filename in urls:
            existing_files = self.file_manager.get_existing_csvs()

            # Selenium actions
            self.selenium_client.get_page(url)
            self.selenium_client.click_download_button()
            downloaded_file = self.selenium_client.wait_for_new_file(existing_files)

            # File actions
            final_path = self.file_manager.move_file(downloaded_file, filename)
            df = self.file_manager.read_csv(final_path)
            df = self.file_manager.normalize_headers(df)

            # Mongo actions
            self.mongo_manager.insert_dataframe(df)
