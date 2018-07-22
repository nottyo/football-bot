from flask import Flask, request, abort, jsonify
import sys
import os
import json
import feedparser
from rss_feed import RssFeed
from football_news import FootballNews
from football_api import FootballApi

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
football_api = FootballApi()

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

MAIN_MENU_CHAT_BAR = 'MainMenu'
RESULTS_CHAT_BAR = 'Results'
FIXTURES_CHAT_BAR = 'Fixtures'
TEAM_NEWS_CHAT_BAR = 'Team News'
TEAM_CHAT_BAR = 'Team'
STANDINGS_CHAT_BAR = 'Standings'

fixtures_header_color = {
    'pl': '#3D185B',
    'ucl': '#231F20',
    'laliga': '#FF7D01',
    'bundesliga': '#D20514',
    'calcio': '#098D37'
}


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


@app.route('/news/dailymail/<limit>')
def get_dailymail_news(limit):
    data = rss_feed.get_daily_mail_feed(int(limit))
    return jsonify(data)


def get_all_news(reply_token):
    print('handle_postback: news=all')
    carousel_template = CarouselContainer()
    # bbc-sport
    bbc_data = rss_feed.get_bbc_feed(5)
    carousel_template.contents.append(football_news.get_news_bubble("#FEE63E", bbc_data))
    print('news=all, bbc-sport completed')
    # sky-sport
    sky_data = rss_feed.get_skysports_feed(5)
    carousel_template.contents.append(football_news.get_news_bubble("#BB0211", sky_data, header_text_color="#ffffff"))
    print('news=all, sky-sports completed')
    # guardian
    guardian_data = rss_feed.get_guardian_feed(5)
    carousel_template.contents.append(
        football_news.get_news_bubble("#09508D", guardian_data, header_text_color="#ffffff"))
    print('news=all, guardian completed')
    # mirror
    mirror_data = rss_feed.get_mirror_feed(5)
    carousel_template.contents.append(
        football_news.get_news_bubble("#E80E0D", mirror_data, header_text_color="#ffffff"))
    print('news=all, mirror completed')
    # goal-com
    goal_data = rss_feed.get_goal_feed(5)
    carousel_template.contents.append(
        football_news.get_news_bubble("#091F2C", goal_data, header_text_color="#ffffff"))
    print('news=all, goal-com completed')
    # shotongoal
    shotongoal_data = rss_feed.get_shot_on_goal_feed(5)
    carousel_template.contents.append(
        football_news.get_news_bubble("#1A1A1A", shotongoal_data, header_text_color="#ffffff"))
    print('news=all, shotongoal completed')
    # soccersuck
    soccersuck_data = rss_feed.get_soccersuck_feed(5)
    carousel_template.contents.append(
        football_news.get_news_bubble("#197F4D", soccersuck_data))
    print('news=all, soccersuck completed')

    line_bot_api.reply_message(reply_token, FlexSendMessage(alt_text='AllNews', contents=carousel_template))


def _transition_rich_menu(user_id, to):
    rich_menu_list = line_bot_api.get_rich_menu_list()
    line_bot_api.unlink_rich_menu_from_user(user_id)
    for rich_menu in rich_menu_list:
        if rich_menu.chat_bar_text == to:
            print('linking richmenu: \"{0}\" to user_id: {1}'.format(rich_menu.chat_bar_text, user_id))
            line_bot_api.link_rich_menu_to_user(user_id, rich_menu.rich_menu_id)


def handle_fixtures(event):
    print('handle_fixtures')
    data = event.postback.data
    league_name = str(data).split('=')[1]
    fixtures_data = football_api.get_fixtures(league_name)
    print(json.dumps(fixtures_data))
    if len(fixtures_data) > 3:
        # carousel template
        carousel_container = CarouselContainer()
        for date, data in fixtures_data.items():
            print('date: {}'.format(date))
            print('data: {}'.format(data))
            bubble = {
                "type": "bubble",
                "styles": {
                    "header": {
                        "backgroundColor": fixtures_header_color[league_name]
                    },
                    "body": {
                        "separator": True
                    }
                },
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "weight": "bold",
                            "text": "{0} - Matchday #{1}".format(fixtures_data['competition_name'], fixtures_data['match_day']),
                            "color": "#ffffff"
                        }
                    ]
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "text",
                            "text": date,
                            "size": "sm",
                            "weight": "bold",
                            "align": "center"
                        },
                        {
                            "type": "separator"
                        }
                    ]
                }
            }
            bubble_contents = bubble['body']['contents']
            if isinstance(data, list):
                for match in data:
                    bubble_contents.append(
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "size": "xxs",
                                    "text": match['homeTeam']['name'],
                                    "flex": 3,
                                    "wrap": True,
                                    "action": {
                                        "type": "postback",
                                        "data": "team_id={0}".format(match['homeTeam']['id'])
                                    }
                                },
                                {
                                    "type": "text",
                                    "size": "xxs",
                                    "text": match['match_time'],
                                    "flex": 1,
                                    "action": {
                                        "type": "postback",
                                        "data": "match_id={0}".format(match['match_id'])
                                    }
                                },
                                {
                                    "type": "text",
                                    "size": "xxs",
                                    "text": match['awayTeam']['name'],
                                    "flex": 3,
                                    "wrap": True,
                                    "action": {
                                        "type": "postback",
                                        "data": "team_id={0}".format(match['awayTeam']['id'])
                                    }
                                }
                            ]
                        }
                    )
                carousel_container.contents.append(bubble)

        line_bot_api.reply_message(event.reply_token, messages=FlexSendMessage(alt_text='Fixtures',
                                                                               contents=carousel_container))

    if len(fixtures_data) == 3:
        # just bubble
        print('just bubble')




def handle_results(event):
    print('handle_results')


def handle_teams(event):
    print('handle_teams')


def handle_team_news(event):
    print('handle_team_news')


def handle_standings(event):
    print('handle_standings')


@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    print('postback.data: {}'.format(data))
    if data == 'news=all':
        get_all_news(event.reply_token)
    if data == 'go=results':
        _transition_rich_menu(event.source.user_id, RESULTS_CHAT_BAR)
    if data == 'go=fixtures':
        _transition_rich_menu(event.source.user_id, FIXTURES_CHAT_BAR)
    if data == 'go=team_news':
        _transition_rich_menu(event.source.user_id, TEAM_NEWS_CHAT_BAR)
    if data == 'go=team':
        _transition_rich_menu(event.source.user_id, TEAM_CHAT_BAR)
    if data == 'go=standings':
        _transition_rich_menu(event.source.user_id, STANDINGS_CHAT_BAR)
    if 'fixtures=' in data:
        handle_fixtures(event)
    if data == 'go=back':
        _transition_rich_menu(event.source.user_id, MAIN_MENU_CHAT_BAR)


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    result = ''

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
    if text.lower() == 'news=dailymail':
        data = rss_feed.get_daily_mail_feed(5)
        result = football_news.get_news_bubble("#ffffff", data)

    if isinstance(result, BubbleContainer):
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text='news', contents=result))


@handler.add(FollowEvent)
def handle_follow(event):
    _transition_rich_menu(event.source.user_id, MAIN_MENU_CHAT_BAR)


if __name__ == '__main__':
    app.run(debug=True)
