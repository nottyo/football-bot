import os
import sys
from time import time

import requests
from flask import Flask, request, abort, jsonify, render_template
from flask_bootstrap import Bootstrap
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    SourceUser, SourceGroup, SourceRoom,
    MessageEvent, TextMessage, TextSendMessage,
    PostbackEvent,
    FollowEvent, FlexSendMessage, BubbleContainer, CarouselContainer
)

from football_api import FootballApi
from football_news import FootballNews
from rss_feed import RssFeed

app = Flask(__name__)
bootstrap = Bootstrap(app)
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

team_name_dict = {
    'manutd': '66',
    'arsenal': '57',
    'liverpool': '64',
    'chelsea': '61',
    'mancity': '65'
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

@app.route('/liff')
def handle_liff():
    return render_template('index.html')

@app.route('/live', methods=['GET'])
def handle_live():
    to = request.args.get('id')
    data = rss_feed.get_live_feed()
    if len(data) > 0:
        carousel_data = rss_feed.create_live_flxed(data['data'])
        if carousel_data is not None:
            carousel_message = CarouselContainer.new_from_json_dict(carousel_data)
            line_bot_api.push_message(to=to, messages=FlexSendMessage(alt_text="โปรแกรมถ่ายทอดสดฟุตบอล", contents=carousel_message))
    return jsonify({'status': 'ok'})


def print_source(event):
    if isinstance(event.source, SourceUser):
        print('user_id: {0}'.format(event.source.user_id))
    if isinstance(event.source, SourceRoom):
        print('room_id: {0}'.format(event.source.room_id))
    if isinstance(event.source, SourceGroup):
        print('group_id: {0}'.format(event.source.group_id))


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
    carousel_template.contents.append(football_news.get_news_bubble("#FEE63E", bbc_data, header_text_color="#000000"))
    print('news=all, bbc-sport completed')
    # sky-sport
    sky_data = rss_feed.get_skysports_feed(5)
    carousel_template.contents.append(football_news.get_news_bubble("#BB0211", sky_data))
    print('news=all, sky-sports completed')
    # guardian
    guardian_data = rss_feed.get_guardian_feed(5)
    carousel_template.contents.append(
        football_news.get_news_bubble("#09508D", guardian_data))
    print('news=all, guardian completed')
    # mirror
    mirror_data = rss_feed.get_mirror_feed(5)
    carousel_template.contents.append(
        football_news.get_news_bubble("#E80E0D", mirror_data))
    print('news=all, mirror completed')
    # goal-com
    goal_data = rss_feed.get_goal_feed(5)
    carousel_template.contents.append(
        football_news.get_news_bubble("#091F2C", goal_data))
    print('news=all, goal-com completed')
    # shotongoal
    shotongoal_data = rss_feed.get_shot_on_goal_feed(5)
    carousel_template.contents.append(
        football_news.get_news_bubble("#1A1A1A", shotongoal_data))
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
    data = event.postback.data
    league_name = str(data).split('=')[1]
    fixtures_data = football_api.get_fixtures(league_name)
    if len(fixtures_data) == 2:
        line_bot_api.reply_message(event.reply_token, messages=TextSendMessage(text='No Fixtures In MatchDay {0}'.format(fixtures_data['match_day'])))
        return
    # carousel template
    carousel_container = CarouselContainer()
    for date, data in fixtures_data.items():
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
                        "text": "{0} - Matchday #{1}".format(fixtures_data['competition_name'],
                                                             fixtures_data['match_day']),
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
                                    "data": "matches_by_team={0}".format(match['homeTeam']['id'])
                                }
                            },
                            {
                                "type": "text",
                                "size": "xxs",
                                "text": match['match_time'],
                                "flex": 1,
                                "action": {
                                    "type": "postback",
                                    "data": "match={0}".format(match['match_id'])
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
                                    "data": "matches_by_team={0}".format(match['awayTeam']['id'])
                                }
                            }
                        ]
                    }
                )
            carousel_container.contents.append(bubble)

    line_bot_api.reply_message(event.reply_token, messages=FlexSendMessage(alt_text='Fixtures',
                                                                           contents=carousel_container))


def handle_results(event):
    print('handle_results')
    data = event.postback.data
    league_name = str(data).split('=')[1]
    fixtures_data = football_api.get_results(league_name, 7)
    if len(fixtures_data) == 1:
        line_bot_api.reply_message(event.reply_token, messages=TextSendMessage(text='No Result'))
        return
    # carousel template
    carousel_container = CarouselContainer()
    for date, data in fixtures_data.items():
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
                        "text": "{0} Results".format(fixtures_data['competition_name']),
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
                                    "data": "team={0}".format(match['homeTeam']['id'])
                                }
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 2,
                                "contents": [
                                    {
                                        "type": "text",
                                        "size": "xxs",
                                        "wrap": True,
                                        "weight": "bold",
                                        "text": "{0} ({1})".format(match['score'], match['status']),
                                        "action": {
                                            "type": "postback",
                                            "data": "match={0}".format(match['match_id'])
                                        }
                                    }
                                ]
                            }
                            ,
                            {
                                "type": "text",
                                "size": "xxs",
                                "text": match['awayTeam']['name'],
                                "flex": 3,
                                "wrap": True,
                                "action": {
                                    "type": "postback",
                                    "data": "team={0}".format(match['awayTeam']['id'])
                                }
                            }
                        ]
                    }
                )
            carousel_container.contents.append(bubble)

    line_bot_api.reply_message(event.reply_token, messages=FlexSendMessage(alt_text='Results',
                                                                           contents=carousel_container))


def handle_teams(event):
    print('handle_teams')
    postback_data = event.postback.data
    team_id = postback_data.split('=')[1]
    team_data = football_api.get_team(team_id)
    carousel = CarouselContainer()
    pages = [team_data['players'][i: i+10] for i in range(0, len(team_data['players']), 10)]
    for page in pages:
        bubble = {
            "type": "bubble",
            "styles": {
                "header": {
                    "backgroundColor": "#4a4b4c"
                }
            },
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": team_data["team_name"],
                        "weight": "bold",
                        "size": "md",
                        "color": "#ffffff",
                        "action": {
                            "type": "uri",
                            "uri": team_data["team_website"]
                        }
                    },
                    {
                        "type": "text",
                        "text": "Coach: {}".format(team_data["head_coach"]),
                        "size": "xs",
                        "color": "#ffffff"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "Full Name",
                                "weight": "bold",
                                "size": "xxs",
                                "flex": 5
                            },
                            {
                                "type": "text",
                                "text": "Position",
                                "weight": "bold",
                                "size": "xxs",
                                "flex": 2
                            },
                            {
                                "type": "text",
                                "text": "Age",
                                "weight": "bold",
                                "size": "xxs",
                                "flex": 1
                            }
                        ]
                    },
                    {
                        "type": "separator"
                    }
                ]
            }
        }
        body_contents = bubble['body']['contents']
        for player in page:
            body_contents.append(
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": player['name'],
                            "size": "xxs",
                            "wrap": True,
                            "flex": 5
                        },
                        {
                            "type": "text",
                            "text": player['position'],
                            "size": "xxs",
                            "flex": 2
                        },
                        {
                            "type": "text",
                            "text": str(player['age']),
                            "size": "xxs",
                            "flex": 1
                        }
                    ]
                }
            )
            bubble_container = BubbleContainer.new_from_json_dict(bubble)
        carousel.contents.append(bubble_container)
    line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text='Team', contents=carousel))


def handle_team_news(event):
    data = event.postback.data
    if data == 'team_news=manutd':
        manutd_news = rss_feed.get_manutd_feed(5)
        manutd_result = football_news.get_news_bubble("#DC1F29", manutd_news)
        line_bot_api.reply_message(event.reply_token, messages=FlexSendMessage(alt_text='Manchester United News', contents=manutd_result))
    if data == 'team_news=arsenal':
        arsenal_news = rss_feed.get_arsenal_feed(5)
        arsenal_result = football_news.get_news_bubble("#EC0C1C", arsenal_news)
        line_bot_api.reply_message(event.reply_token,
                                   messages=FlexSendMessage(alt_text='Arsenal News', contents=arsenal_result))
    if data == 'team_news=liverpool':
        liverpool_news = rss_feed.get_liverpool_feed(5)
        liverpool_result = football_news.get_news_bubble("#C8102E", liverpool_news)
        line_bot_api.reply_message(event.reply_token,
                                   messages=FlexSendMessage(alt_text='Liverpool News', contents=liverpool_result))
    if data == 'team_news=chelsea':
        chelsea_news = rss_feed.get_chelsea_feed(5)
        chelsea_result = football_news.get_news_bubble("#034694", chelsea_news)
        line_bot_api.reply_message(event.reply_token,
                                   messages=FlexSendMessage(alt_text='Chelsea News', contents=chelsea_result))
    if data == 'team_news=mancity':
        mancity_news = rss_feed.get_mancity_feed(5)
        mancity_result = football_news.get_news_bubble("#99C5E7", mancity_news)
        line_bot_api.reply_message(event.reply_token,
                                   messages=FlexSendMessage(alt_text='Manchester City News', contents=mancity_result))

    print('handle_team_news')


def handle_standings(event):
    print('handle_standings')
    data = event.postback.data
    league_name = str(data).split('=')[1]
    standings_data = football_api.get_standings(league_name)
    if len(standings_data['teams']) == 0:
        line_bot_api.reply_message(event.reply_token, messages=TextSendMessage(text='No Standings Data'))
        return
    carousel = CarouselContainer()
    pages = [standings_data['teams'][i: i+10] for i in range(0, len(standings_data['teams']), 10)]
    for page in pages:
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
                        "text": "{0} - Standings".format(standings_data['competition_name']),
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
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "#",
                                "size": "xs",
                                "weight": "bold",
                                "flex": 2
                            },
                            {
                                "type": "text",
                                "text": "Team",
                                "size": "xs",
                                "weight": "bold",
                                "flex": 11
                            },
                            {
                                "type": "text",
                                "text": "P",
                                "size": "xs",
                                "weight": "bold",
                                "flex": 2
                            },
                            {
                                "type": "text",
                                "text": "Pts",
                                "size": "xs",
                                "weight": "bold",
                                "flex": 3
                            }
                        ]
                    },
                    {
                        "type": "separator"
                    }
                ]
            }
        }
        bubble_body_contents = bubble['body']['contents']
        for team in page:
            bubble_body_contents.append(
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": team['position'],
                            "size": "xxs",
                            "flex": 2
                        },
                        {
                            "type": "text",
                            "text": team['team_name'],
                            "size": "xxs",
                            "wrap": True,
                            "flex": 11,
                            "action": {
                                "type": "postback",
                                "data": "team={}".format(team['team_id'])
                            }
                        },
                        {
                            "type": "text",
                            "text": team['played'],
                            "size": "xxs",
                            "flex": 2
                        },
                        {
                            "type": "text",
                            "text": team['pts'],
                            "size": "xxs",
                            "flex": 3
                        }
                    ]
                }
            )
            bubble_container = BubbleContainer.new_from_json_dict(bubble)
        carousel.contents.append(bubble_container)
    line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text='Standings', contents=carousel))


def handle_matches_by_team(event):
    print('handle_matches_by_team')
    team_id = event.postback.data.split('=')[1]
    team_fixtures = football_api.get_matches_by_team(team_id, 5)
    bubble = {
        "type": "bubble",
        "styles": {
            "header": {
                "backgroundColor": "#007a12"
            }
        },
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "{0} Fixtures".format(team_fixtures['team_name']),
                    "weight": "bold",
                    "wrap": True,
                    "color": "#ffffff",
                    "size": "md",
                    "action": {
                        "type": "postback",
                        "data": "team={0}".format(team_id)
                    }
                }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "Upcoming Matches",
                    "weight": "bold",
                    "size": "xs",
                    "align": "start"
                },
                {
                    "type": "separator"
                }
            ]
        }
    }
    bubble_body_contents = bubble['body']['contents']
    for match in team_fixtures['matches']:
        bubble_body_contents.append(
            {
                "type": "box",
                "layout": "horizontal",
                "spacing": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": match['dt'],
                        "wrap": True,
                        "size": "xxs",
                        "flex": 2
                    },
                    {
                        "type": "separator"
                    },
                    {
                        "type": "text",
                        "text": match['opponent_team_name'],
                        "size": "xs",
                        "wrap": True,
                        "flex": 5,
                        "action": {
                            "type": "postback",
                            "data": "matches_by_team={0}".format(match['opponent_team_id'])
                        }
                    }
                ]
            }
        )
        bubble_body_contents.append(
            {
                "type": "separator"
            }
        )
    bubble_container = BubbleContainer.new_from_json_dict(bubble)
    line_bot_api.reply_message(event.reply_token, messages=FlexSendMessage(alt_text='Team Fixtures', contents=bubble_container))
    
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
    if data == 'go=back':
        _transition_rich_menu(event.source.user_id, MAIN_MENU_CHAT_BAR)
    if 'results=' in data:
        handle_results(event)
    if 'fixtures=' in data:
        handle_fixtures(event)
    if 'standings=' in data:
        handle_standings(event)
    if 'matches_by_team=' in data:
        handle_matches_by_team(event)
    elif 'team_news=' in data:
        handle_team_news(event)
    elif 'team=' in data:
        handle_teams(event)
    
def print_help(event):
    help = """Usage():
    @bot help
    @bot allnews
    @bot results=<league_name>
    @bot fixtures=<league_name>
    @bot teamnews=<team_name>
    @bot team=<team_name>
    @bot standings=<league_name>

    <league_name> = pl | ucl | bundesliga | laliga | calcio
    <team_name> = manutd | arsenal | liverpool | chelsea | mancity
    """
    line_bot_api.reply_message(event.reply_token, messages=TextSendMessage(text=help))

def get_liff_app(endpoint):
    url = 'https://api.line.me/liff/v1/apps'
    headers = {
        'Authorization': 'Bearer {}'.format(channel_access_token) 
    }
    response = requests.get(url, headers=headers)
    resp_json = response.json()
    for app in resp_json['apps']:
        if endpoint in app['view']['url']:
            return 'line://app/{}'.format(app['liffId'])
    return ''


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    print_source(event)
    result = ''

    if text.lower() == 'liff':
        line_bot_api.reply_message(event.reply_token, messages=TextSendMessage(text=get_liff_app('/liff')))
        return
    if 'live' in text.lower():
        data = rss_feed.get_live_feed()
        if len(data) > 0:
            carousel_data = rss_feed.create_live_flxed(data['data'])
            if carousel_data is not None:
                carousel_message = CarouselContainer.new_from_json_dict(carousel_data)
                line_bot_api.reply_message(event.reply_token, messages=FlexSendMessage(alt_text="โปรแกรมถ่ายทอดสดฟุตบอล", contents=carousel_message))

    if text.lower() == '@bot help':
        print_help(event)
        return
    if '@bot results=' in text.lower():
        league_name = text.lower().split('=')[1]
        if league_name in fixtures_header_color:
            results_pb = PostbackEvent(timestamp=time(), source=event.source, reply_token=event.reply_token,
            postback={
                'data': 'results={0}'.format(league_name)
            })
            handle_results(results_pb)
        else:
            print_help(event)
    if '@bot fixtures=' in text.lower():
        league_name = text.lower().split('=')[1]
        if league_name in fixtures_header_color:
            fixtures_pb = PostbackEvent(timestamp=time(), source=event.source, reply_token=event.reply_token,
            postback={
                'data': 'fixtures={0}'.format(league_name)
            })
            handle_fixtures(fixtures_pb)
        else:
            print_help(event)
    if '@bot teamnews=' in text.lower():
        team_name = text.lower().split('=')[1]
        if team_name in team_name_dict:
            teamnews_pb = PostbackEvent(timestamp=time(), source=event.source, reply_token=event.reply_token,
            postback={
                'data': 'team_news={0}'.format(team_name)
            })
            handle_team_news(teamnews_pb)
        else:
            print_help(event)
    if '@bot team=' in text.lower():
        team_name = text.lower().split('=')[1]
        if team_name in team_name_dict:
            team_pb = PostbackEvent(timestamp=time(), source=event.source, reply_token=event.reply_token,
            postback={
                'data': 'team={0}'.format(team_name_dict[team_name])
            })
            handle_teams(team_pb)
        else:
            print_help(event)
    if '@bot standings=' in text.lower():
        league_name = text.lower().split('=')[1]
        if league_name in fixtures_header_color:
            standings_pb = PostbackEvent(timestamp=time(), source=event.source, reply_token=event.reply_token,
            postback={
                'data': 'standings={0}'.format(league_name)
            })
            handle_standings(standings_pb)
        else:
            print_help(event)

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
    if text.lower() == '@bot allnews':
        get_all_news(event.reply_token)

    if isinstance(result, BubbleContainer):
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text='news', contents=result))


@handler.add(FollowEvent)
def handle_follow(event):
    _transition_rich_menu(event.source.user_id, MAIN_MENU_CHAT_BAR)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
