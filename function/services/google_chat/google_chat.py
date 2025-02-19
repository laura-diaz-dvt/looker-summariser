import requests

class MyException(Exception):
    pass

class GoogleChat:
    def __init__(self, webhook):
        self.webhook_url = webhook
        self.headers = {"Content-Type": "application/json; charset=UTF-8"}

    def create_message(self, summaries, pdf_url):
        """
        Creates the message to be sent into Google chat using the attachment url and summaries
        
        Input:
        summaries: List
        pdf_url: Str
        
        Output:
        List
        """

        widgets = []
        for summary in summaries:
            widgets.extend([{"textParagraph": {"text": summary}}, {"divider": {}}])

        widgets.append({
            "buttonList": {
                "buttons": [
                {
                    "text": "Get PDF Attachment",
                    "onClick": {
                    "openLink": {
                        "url": pdf_url
                    }
                    }
                }
                ]
            }
        })

        message = {
            "cardsV2": [
                {
                    "cardId": "dashboard_summary_card",
                    "card": {
                        "sections": [
                            {
                                "widgets": widgets
                            }
                        ],
                    },
                }
            ]
        }
        return message

    def send_message(self, message):
        """
        Posts the message to Google chat

        Input:
        message: Str
        """
        try:
            response = requests.post(self.webhook_url, headers=self.headers, json=message)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise MyException(e)