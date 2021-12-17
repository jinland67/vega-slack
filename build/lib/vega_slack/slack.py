from slack_sdk.webhook import WebhookClient
from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler


class SlackError(Exception):
    #------------------------------------------------
    # 생성할 때 value 값을 입력 받은다.
    # -----------------------------------------------
    def __init__(self, value):
        self.value = value

    #------------------------------------------------
    # 생성할 때 받은 value 값을 확인 한다.
    # -----------------------------------------------
    def __str__(self):
        return self.value


class Slack:
    def __init__(self, url):
        self.__url = url

    def send(self, block):
        try:
            webhook = WebhookClient(url=self.__url)
            rate_limit_handler = RateLimitErrorRetryHandler(max_retry_count=1)
            webhook.retry_handlers.append(rate_limit_handler)
            # message send
            response = webhook.send(
                text="fallback",
                blocks=block
            )
            # assert response.status_code == 200
            if response.status_code != 200:
                msg = 'Request to slack returned an error %s, the response is %s' % (response.status_code, response.text)
                raise SlackError(msg)
        except Exception as e:
            msg = f"Slack exception occured in send(). type: {type(e)}, message: {str(e)}"
            raise SlackError(msg)


