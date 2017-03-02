import json
import os

from flask import Flask, request, abort
import urllib.request
from bs4 import BeautifulSoup

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import settings


class Event:
    def __init__(self, event):
        self.event = event
        self.type = event.type
        self.timestamp = event.timestamp
        self.reply_token = event.reply_token
        self.source = event.source
        self.source_type = event.source.type
        if self.source_type == 'user':
            self.source_id = event.source.user_id
        elif self.source_type == 'group':
            self.source_id = event.source.group_id
        self.message = event.message
        self.message_type = event.message.type
        self.message_text = event.message.text

    def reply(self, text):
        line_bot_api.reply_message(self.reply_token, TextSendMessage(text=text))


app = Flask(__name__)
line_bot_api = LineBotApi(settings.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.CHANNEL_SECRET)
prev_message = ''


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@app.route('/update', methods=['GET'])
def update():
    os.system('sh update.sh')
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(event)
    e = Event(event)
    global prev_message
    if prev_message == e.message_text:
        e.reply(prev_message)
        return

    prev_message = e.message_text
    if '환율' in e.message_text:
        reply_exchange(e)
    elif '인테일러' == e.message_text:
        e.reply('고약한놈!')
    elif '테일러' in e.message_text:
        e.reply('보스 미니 2만원에 삽니다')
    elif '2만엔' in e.message_text:
        e.reply('2만원')
    elif '프할배' in e.message_text:
        e.reply('이제 노인학대 그만하시죳')
    elif '지수' in e.message_text:
        e.reply('병특회사는 안녕하십니까')
    elif '데이트' in e.message_text:
        e.reply('연애하고 싶네욧...ㅜ')
    elif '륜카' in e.message_text:
        e.reply('기름 넣어 준다고요? +_+')
    elif '티맵' in e.message_text:
        e.reply('티맵 안써요 -ㅅ-')
    elif '풀러스' in e.message_text:
        e.reply('마이너수')
    elif '인용휘' in e.message_text:
        e.reply('인용휘(이)가 나타났다!!!')
    elif '에구' in e.message_text:
        e.reply('머니나')
    elif '저런' in e.message_text:
        e.reply('좋지않아')
    elif '박치완' in e.message_text:
        e.reply('그분은 바쁩니다')
    elif '와니' in e.message_text:
        e.reply('그분은 바쁩니다')
    elif '전박사' in e.message_text:
        e.reply('그분의 이름을 불러서는 안돼')
    elif '승원' in e.message_text:
        e.reply('프할배 굴러가는 소리좀 안나게 해라!')
    elif '한진수' in e.message_text:
        e.reply('진수짜응')
    elif len(e.message_text) == 2 and e.message_text[0] == e.message_text[1]:
        e.reply(e.message_text)
    elif '날씨' in e.message_text:
        reply_weather(e)


def reply_exchange(e):
    fp = urllib.request.urlopen(
        'http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.xchange%20where%20pair%3D%22USDKRW,JPYKRW,EURKRW,GBPKRW,CNYKRW,CHFKRW%22&format=json&diagnostics=false&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys')
    exchange = json.loads(fp.read().decode("utf8"))
    fp.close()

    s = '[현재 환율!]'
    for c in exchange['query']['results']['rate']:
        if c['Name'] == 'JPY/KRW':
            s += '\n' + c['Name'][:3] + ': ' + '{0:.2f}'.format(float(c['Rate']) * 100)
        else:
            s += '\n' + c['Name'][:3] + ': ' + '{0:.2f}'.format(float(c['Rate']))
    e.reply(s)


# def reply_weather(e):
#     fp = urllib.request.urlopen(
#         'http://www.kweather.co.kr/forecast/forecast_lifestyle.html')
#     body = fp.read()
#     fp.close()
#
#     soup = BeautifulSoup(body, 'html.parser')
#     e.reply(soup.find(class_='lifestyle_condition_content').text.strip())


if __name__ == "__main__":
    app.run(host='0.0.0.0')
