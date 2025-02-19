import requests

class MyException(Exception):
    pass

class Slack:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.headers = {"Content-Type": "application/json; charset=UTF-8"}

    def create_message(self, summaries, attachment_url):
        """
        Creates a message for Slack using the summaries and provided attachment URL

        Args:
            summaries (List[Str]): List of strings containing the summaries per tile.
            attachment_url (Str): URL of the attachment
        """
        blocks = []
        last_item = summaries[-1]
        for summary in summaries:
            if not summary == last_item:
                blocks.extend([{"type": "section", "text": {"type": "plain_text", "text": summary, "emoji": True}}, {"type": "divider"}])
            else:
                blocks.extend([
                    {
                        "type": "section", 
                        "text": {"type": "plain_text", "text": summary, "emoji": True}, 
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Get PDF Attachment",
                                    "emoji": True
                                },
                                "value": "click_me_123",
                                "action_id": "actionId-0",
                                "url": attachment_url
                            }
                        ]
                    }
                ])

        return {"blocks": blocks}

    def send_message(self, message):
        """
        Sends the message to the slack webhook. Returns an error if fails

        Args:
            message (Dict): Dictionary of the message to send
        """
        try:
            response = requests.post(self.webhook_url, headers=self.headers, json=message)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise MyException(e)