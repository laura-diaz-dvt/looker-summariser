import requests

class MyException(Exception):
    pass

class Teams:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.headers = {"Content-Type": "application/json; charset=UTF-8"}

    def create_message(self, summaries, attachment_url):
        """
        Creates a message for Teams using the summaries and provided attachment URL

        Args:
            summaries (List[Str]): List of strings containing the summaries per tile.
            attachment_url (Str): URL of the attachment
        """
        blocks = []
        last_item = summaries[-1]
        for summary in summaries:
            if not summary == last_item:
                blocks.append({"type": "Container", "items": [{"type": "TextBlock", "text": summary, "wrap": True}]})
            else:
                blocks.extend([
                    {
                        "type": "Container",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": summary,
                                "wrap": True
                            }
                        ]
                    },
                    {
                        "type": "ActionSet",
                        "actions": [
                            {
                                "type": "Action.OpenUrl",
                                "title": "PDF Attachment",
                                "url": attachment_url
                            }
                        ]
                    }
                ])

        return {"type": "AdaptiveCard", "body": blocks, "$schema": "http://adaptivecards.io/schemas/adaptive-card.json", "version": "1.5"}

    def send_message(self, message):
        """
        Sends the message to the teams webhook. Returns an error if fails

        Args:
            message (Dict): Dictionary of the message to send
        """
        try:
            response = requests.post(self.webhook_url, headers=self.headers, json=message)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise MyException(e)