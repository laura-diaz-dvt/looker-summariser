import google.cloud.logging
import logging


class Logger:
    def __init__(self, project_id):
        self.project_id = project_id

        self.client = google.cloud.logging.Client()
        self.client.setup_logging()

    def log(self, text):
        logging.info(text)
