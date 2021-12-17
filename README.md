# vega_slack
> slack message 전송을 위한 라이브러리

    * 의존성:
        - python 3.8.10 이상
        - slack-sdk 3.13.0 이상

------------------
### 사용법
```
    # install
        $  pip install git+https://github.com/jinland67/vega-slack.git

    # chromedriver 사용 시
        from vega_slack import Slack, SlackError
                :
                :
        slack = Slack(url)
                :
        slack.send(blocks)
```

### blocks sample
```
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "헤더 영역에 작성할 메시지"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "타이틀 영역에 작성할 메시지"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "섹션 영역에 작성할 메시지"
            }
        }
    ]
```

