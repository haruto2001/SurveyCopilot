from typing import Union

import requests

from modules.paper import Paper


class SlackNotifier:
    """
    A class for sending messages to a Slack channel using the Slack API.

    Attributes:
        bot_token (str): The Slack bot token for authentication.
        channel (str): The Slack channel where messages will be sent.
        icon_emoji (str): The emoji icon to display with messages.
        thread_ts (str or None): The thread timestamp for replying to a thread.
        url (str): The Slack API URL for sending messages.
        headers (dict): The headers for the Slack API request.
    """

    def __init__(
        self,
        bot_token: str,
        channel: str = "dev-survey-copilot",
        icon_emoji: str = ":ghost:",
    ) -> None:
        """
        Initializes the SlackNotifier with the given bot token, channel, and icon emoji.

        Args:
            bot_token (str): The Slack bot token for authentication.
            channel (str, optional): The Slack channel where messages will be sent. Defaults to "dev-survey-copilot".
            icon_emoji (str, optional): The emoji icon to display with messages. Defaults to ":ghost:".
        """
        self.bot_token = bot_token
        self.channel = channel
        self.icon_emoji = icon_emoji

        self.thread_ts = None
        self.url = "https://slack.com/api/chat.postMessage"
        self.headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json",
        }

    def send_message(self, message: str) -> None:
        """
        Sends a message to the Slack channel.

        Args:
            message (str): The message to send.

        Raises:
            RuntimeError: If the request to Slack fails or if the response is malformed.
        """
        payload = self._build_payload(message=message)
        try:
            response = requests.post(
                url=self.url,
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            response_data = response.json()
            if "ts" in response_data:
                self.thread_ts = response_data["ts"]
            else:
                raise ValueError("Response does not contain 'ts' key")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to send message to Slack: {e}")
        except ValueError as e:
            raise RuntimeError(f"Unexpected response format: {e}")

    def _build_payload(self, message: str) -> dict:
        """
        Builds the payload for the Slack API request.

        Args:
            message (str): The message to send.

        Returns:
            dict: The payload to send to the Slack API.
        """
        return {
            "text": message,
            "channel": self.channel,
            "icon_emoji": self.icon_emoji,
            "thread_ts": self.thread_ts,
        }


class SlackPaperNotifier(SlackNotifier):
    """
    A subclass of SlackNotifier for sending messages about academic papers.

    Inherits from SlackNotifier and overrides the send_message method to format
    paper details into a message before sending it to the Slack channel.

    Args:
        bot_token (str): The Slack bot token for authentication.
        channel (str, optional): The Slack channel where messages will be sent. Defaults to "dev-survey-copilot".
        icon_emoji (str, optional): The emoji icon to display with messages. Defaults to ":ghost:".
    """

    def __init__(
        self,
        bot_token: str,
        channel: str = "dev-survey-copilot",
        icon_emoji: str = ":ghost:",
    ) -> None:
        """
        Initializes the SlackPaperNotifier with the given bot token, channel, and icon emoji.

        Args:
            bot_token (str): The Slack bot token for authentication.
            channel (str, optional): The Slack channel where messages will be sent. Defaults to "dev-survey-copilot".
            icon_emoji (str, optional): The emoji icon to display with messages. Defaults to ":ghost:".
        """
        super().__init__(bot_token=bot_token, channel=channel, icon_emoji=icon_emoji)

    def send_message(self, message: Union[str, Paper]) -> None:
        """
        Sends a message containing the details of an academic paper to the Slack channel.

        Args:
            message (Union[str, Paper]): The Paper object containing the paper's details to send.
        """
        if isinstance(message, Paper):
            message = self._build_message(paper=message)
        super().send_message(message=message)

    def _build_message(self, paper: Paper) -> str:
        """
        Builds the message to send about a paper.

        Args:
            paper (Paper): The Paper object containing the paper's details.

        Returns:
            str: The formatted message containing the paper's title, authors, and abstract.
        """
        message = f"Title: {paper.title}\nAuthors: {', '.join(paper.authors)}\nAbstract: {paper.abstract}"
        return message
