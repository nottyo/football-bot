from flask import Flask, request, abort, jsonify
import sys
import os
import json
import feedparser
from rss_feed import RssFeed
from football_news import FootballNews

from linebot import (
    LineBotApi, WebhookHandler
)

from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, CarouselContainer
)



app = Flask(__name__)
rss_feed = RssFeed()
football_news = FootballNews()

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


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
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/news/bbc/<limit>')
def get_bbc_news(limit):
    data = rss_feed.get_bbc_feed(int(limit))
    return jsonify(data)


@app.route('/news/skysports/<limit>')
def get_skysports_news(limit):
    data = rss_feed.get_skysports_feed(int(limit))
    return jsonify(data)


@app.route('/news/goal/<limit>')
def get_goal_news(limit):
    data = rss_feed.get_goal_feed(int(limit))
    return jsonify(data)


@app.route('/news/guardian/<limit>')
def get_guardian_news(limit):
    data = rss_feed.get_guardian_feed(int(limit))
    return jsonify(data)


@app.route('/news/mirror/<limit>')
def get_mirror_news(limit):
    data = rss_feed.get_mirror_feed(int(limit))
    return jsonify(data)


@app.route('/news/shotongoal/<limit>')
def get_shotongoal_news(limit):
    data = rss_feed.get_shot_on_goal_feed(int(limit))
    return jsonify(data)


@app.route('/news/soccersuck/<limit>')
def get_soccersuck_news(limit):
    data = rss_feed.get_soccersuck_feed(int(limit))
    return jsonify(data)


def bind_default_rich_menu(event):
    if isinstance(event.source, SourceUser):
        id = event.source.user_id
        rich_menu_list = line_bot_api.get_rich_menu_list()
        for rich_menu in rich_menu_list:
            if rich_menu.chat_bar_text == 'MainMenu':
                line_bot_api.link_rich_menu_to_user(id, rich_menu.rich_menu_id)


@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'news=all':
        print('handle_postback: news=all')
        carousel_template = CarouselContainer()
        # bbc-sport
        bbc_data = rss_feed.get_bbc_feed(5)
        carousel_template.contents.append(football_news.get_news_bubble("#FEE63E", bbc_data))
        # sky-sport
        sky_data = rss_feed.get_skysports_feed(5)
        carousel_template.contents.append(football_news.get_news_bubble("#BB0211", sky_data, header_text_color="#ffffff"))
        # guardian
        guardian_data = rss_feed.get_guardian_feed(5)
        carousel_template.contents.append(
            football_news.get_news_bubble("#09508D", guardian_data, header_text_color="#ffffff"))
        # mirror
        mirror_data = rss_feed.get_mirror_feed(5)
        carousel_template.contents.append(
            football_news.get_news_bubble("#E80E0D", mirror_data, header_text_color="#ffffff"))
        # goal-com
        goal_data = rss_feed.get_goal_feed(5)
        carousel_template.contents.append(
            football_news.get_news_bubble("#091F2C", goal_data, header_text_color="#ffffff"))
        # shotongoal
        shotongoal_data = rss_feed.get_shot_on_goal_feed(5)
        carousel_template.contents.append(
            football_news.get_news_bubble("#1A1A1A", shotongoal_data, header_text_color="#ffffff"))
        # soccersuck
        soccersuck_data = rss_feed.get_soccersuck_feed(5)
        carousel_template.contents.append(
            football_news.get_news_bubble("#197F4D", soccersuck_data))

        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text='AllNews', contents=carousel_template))



@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    result = ''
    bind_default_rich_menu(event)

    if text.lower() == 'news=bbc-sport':
        data = rss_feed.get_bbc_feed(5)
        result = football_news.get_news_bubble("#FEE63E", data)
    if text.lower() == 'news=sky-sport':
        data = rss_feed.get_skysports_feed(5)
        result = football_news.get_news_bubble("#BB0211", data, header_text_color="#ffffff")
    if text.lower() == 'news=goal.com':
        data = rss_feed.get_goal_feed(5)
        result = football_news.get_news_bubble("#091F2C", data, header_text_color="#ffffff")
    if text.lower() == 'news=guardian':
        data = rss_feed.get_guardian_feed(5)
        result = football_news.get_news_bubble("#09508D", data, header_text_color="#ffffff")
    if text.lower() == 'news=mirror':
        data = rss_feed.get_mirror_feed(5)
        result = football_news.get_news_bubble("#E80E0D", data, header_text_color="#ffffff")
    if text.lower() == 'news=shotongoal':
        data = rss_feed.get_shot_on_goal_feed(5)
        result = football_news.get_news_bubble("#1A1A1A", data, header_text_color="#ffffff")
    if text.lower() == 'news=soccersuck':
        data = rss_feed.get_soccersuck_feed(5)
        result = football_news.get_news_bubble("#197F4D", data)

    if isinstance(result, BubbleContainer):
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text='news', contents=result))


@handler.add(FollowEvent)
def handle_follow(event):
    bind_default_rich_menu(event)


if __name__ == '__main__':
    app.run(debug=True)
