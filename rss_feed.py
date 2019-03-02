import feedparser
from datetime import datetime, timedelta
from time import mktime, time
from bs4 import BeautifulSoup
from requests_xml import XMLSession
import os
import ssl
import json
import re
import uuid
import requests
import html2text
import dateparser

BBC_RSS_FEED = 'http://feeds.bbci.co.uk/sport/football/rss.xml'
UK_DATE_FORMAT = '%a, %d %b %Y %H:%M:%S %Z'

SKY_SPORTS_RSS_FEED = 'http://www.skysports.com/rss/11095'
GOAL_RSS_FEED = 'http://www.goal.com/th/feeds/news'
GUARDIAN_RSS_FEED = 'https://www.theguardian.com/football/rss'
MIRROR_RSS_FEED = 'https://www.mirror.co.uk/sport/football/?service=rss'

SHOT_ON_GOAL_RSS_FEED = 'https://www.shotongoal.com/feed/'

SOCCER_SUCK_API = 'http://www.soccersuck.com/api'
SOCCER_SUCK_TOPIC = 'http://www.soccersuck.com/boards/topic'
SOCCER_SUCK_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

DAILY_MAIL_RSS_FEED = 'http://www.dailymail.co.uk/sport/football/index.rss'

MANUTD_RSS_FEED = 'https://www.manutd.com/Feeds/NewsSecondRSSFeed'
ARSENAL_RSS_FEED = 'https://www.90min.com/teams/arsenal.rss'
LIVERPOOL_RSS_FEED = 'https://www.liverpoolfc.com/news.rss'
CHELSEA_RSS_FEED = 'https://www.90min.com/teams/chelsea.rss'
MANCITY_RSS_FEED = 'https://www.90min.com/teams/manchester-city.rss'

session = XMLSession()

class RssFeed(object):

    def __init__(self):
        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context

    def _convert_datetime_to_epoch(self, datetime_str, date_format):
        if 'BST' in datetime_str:
            os.environ['TZ'] = 'Europe/London'
        datetime_obj = datetime.strptime(datetime_str, date_format)
        return int(datetime_obj.timestamp())

    def _format_image_url(self, image_url):
        if str(image_url.startswith('http:')):
            image_url = image_url.replace('http:', 'https:')
        return image_url

    def get_bbc_feed(self, limit):
        d = feedparser.parse(BBC_RSS_FEED)
        data = dict()
        data['feed_title'] = d.feed.title
        data['feed_link'] = d.feed.image.link
        data['feed_date'] = mktime(d.feed.updated_parsed)
        data['entries'] = []
        for index in range(0, limit):
            entry = d.entries[index]
            data['entries'].append(
                {
                    'title': entry['title'],
                    'link': entry['link'],
                    'publish_date': mktime(entry['published_parsed']),
                    'image_url': self._format_image_url(entry['media_thumbnail'][0]['url'])
                }
            )
        data['entries'] = sorted(data['entries'], key=lambda k: k['publish_date'], reverse=True)
        return data

    def get_skysports_feed(self, limit):
        d = feedparser.parse(SKY_SPORTS_RSS_FEED)
        data = dict()
        data['feed_title'] = d.feed.title
        data['feed_link'] = d.feed.image.link
        data['feed_date'] = mktime(d.feed.updated_parsed)
        data['entries'] = []
        d.entries = sorted(d['entries'], key=lambda k: k['published_parsed'], reverse=True)
        for index in range(0, limit):
            entry = d.entries[index]
            data['entries'].append(
                {
                    'title': entry['title'],
                    'link': entry['link'],
                    'publish_date': mktime(entry['published_parsed']),
                    'image_url': self._format_image_url(entry['links'][1]['href'])
                }
            )
        data['entries'] = sorted(data['entries'], key=lambda k: k['publish_date'], reverse=True)
        return data

    def get_daily_mail_feed(self, limit):
        d = feedparser.parse(DAILY_MAIL_RSS_FEED)
        data = dict()
        data['feed_title'] = d.feed.title
        data['feed_link'] = d.feed.image.link
        data['feed_date'] = mktime(d.feed.updated_parsed)
        data['entries'] = []
        d.entries = sorted(d['entries'], key=lambda k: k['published_parsed'], reverse=True)
        for index in range(0, limit):
            entry = d.entries[index]
            data['entries'].append(
                {
                    'title': entry['title'],
                    'link': entry['link'],
                    'publish_date': mktime(entry['published_parsed']),
                    'image_url': self._format_image_url(entry['links'][1]['href'])
                }
            )
        data['entries'] = sorted(data['entries'], key=lambda k: k['publish_date'], reverse=True)
        print('dailymail_data: {0}'.format(data))
        return data

    def get_goal_feed(self, limit):
        d = feedparser.parse(GOAL_RSS_FEED)
        data = dict()
        data['feed_title'] = d.feed.title
        data['feed_link'] = d.feed.link
        data['feed_date'] = mktime(d.feed.updated_parsed)
        data['entries'] = []
        for index in range(0, limit):
            entry = d.entries[index]
            data['entries'].append(
                {
                    'title': entry['title'],
                    'link': entry['link'],
                    'publish_date': mktime(entry['updated_parsed']),
                    'image_url': 'https://upload.wikimedia.org/wikipedia/commons/f/f1/Goal-com-logo-eps-vector-image.png'
                }
            )
        data['entries'] = sorted(data['entries'], key=lambda k: k['publish_date'])
        return data

    def get_guardian_feed(self, limit):
        d = feedparser.parse(GUARDIAN_RSS_FEED)
        data = dict()
        data['feed_title'] = d.feed.title
        data['feed_link'] = d.feed.link
        data['feed_date'] = mktime(d.feed.updated_parsed)
        data['entries'] = []
        for index in range(0, limit):
            entry = d.entries[index]
            data['entries'].append(
                {
                    'title': entry['title'],
                    'link': entry['link'],
                    'publish_date': mktime(entry['updated_parsed']),
                    'image_url': entry['media_content'][1]['url']
                }
            )
        data['entries'] = sorted(data['entries'], key=lambda k: k['publish_date'])
        return data

    def get_mirror_feed(self, limit):
        d = feedparser.parse(MIRROR_RSS_FEED)
        data = dict()
        data['feed_title'] = d.feed.title
        data['feed_link'] = d.feed.link
        data['feed_date'] = mktime(d.feed.updated_parsed)
        data['entries'] = []
        for index in range(0, limit):
            entry = d.entries[index]
            if 'media_content' not in entry:
                image_url = 'https://logos-download.com/wp-content/uploads/2016/06/The_Daily_Mirror_logo_red_background.png'
            else:
                image_url = entry['media_content'][0]['url']
            data['entries'].append(
                {
                    'title': entry['title'],
                    'link': entry['link'],
                    'publish_date': mktime(entry['published_parsed']),
                    'image_url': image_url
                }
            )
        data['entries'] = sorted(data['entries'], key=lambda k: k['publish_date'], reverse=True)
        return data

    def _get_image_url_from_content(self, content, find_str):
        bs = BeautifulSoup(content, 'html.parser')
        images = bs.find_all('img')
        for image in images:
            link = image.get('src')
            if find_str in link:
                return link
        return 'https://www.dwsports.com/on/demandware.static/-/' \
               'Sites-DWS-Master-Catalog/default/dw88d7b256/products/0650288_01.jpeg'

    def get_shot_on_goal_feed(self, limit):
        d = feedparser.parse(SHOT_ON_GOAL_RSS_FEED)
        data = dict()
        data['feed_title'] = d.feed.title
        data['feed_link'] = d.feed.link
        data['feed_date'] = int(time())
        data['entries'] = []
        for index in range(0, limit):
            entry = d.entries[index]
            content = entry['content'][0]['value']
            url = self._get_image_url_from_content(content, 'shotongoal.com')
            data['entries'].append(
                {
                    'title': entry['title'],
                    'link': entry['link'],
                    'publish_date': mktime(entry['published_parsed']),
                    'image_url': url
                }
            )
        data['entries'] = sorted(data['entries'], key=lambda k: k['publish_date'], reverse=True)
        return data

    def _get_access_token(self):
        url = SOCCER_SUCK_API + '/accessToken'
        payload = {
            'secret_key': 'devtab',
            'device_name': 'Xiaomi Mi Pad',
            'device_version': '4.4.4',
            'device_os': 'android',
            'unique_id': str(uuid.uuid4()).split('-')[0]
        }
        response = requests.post(url, data=payload)
        return response.json()['data']['access_token']

    def _check_image_url(self, image_url):
        default_url = "https://is3-ssl.mzstatic.com/image/thumb/Purple118/v4/5a/06/" \
                   "49/5a06491d-2fe1-4805-8474-f3ebdc610266/source/512x512bb.jpg"
        try:
            if str(image_url.startswith('http:')):
                image_url = image_url.replace('http:', 'https:')
            if '[' in image_url or ']' in image_url:
                return default_url
            if str(image_url.startswith('https:')):
                return image_url
            else:
                print("can not get image url: {0}".format(image_url))
                return default_url
        except Exception:
            print("can not get image url: {0}".format(image_url))
            return default_url

    def get_soccersuck_feed(self, limit):
        access_token = self._get_access_token()
        url = SOCCER_SUCK_API + '/latestnews'
        payload = {
            'limit': limit,
            'offset': '0',
            'access_token': access_token
        }
        response = requests.post(url, data=payload)
        resp_json = response.json()
        data = dict()
        data['feed_title'] = 'Soccersuck'
        data['feed_link'] = 'http://soccersuck.com'
        data['feed_date'] = int(time())
        data['entries'] = []
        for index in range(0, limit):
            entry = resp_json['data']['data'][index]
            url = self._check_image_url(entry['image'])
            data['entries'].append(
                {
                    'title': entry['title'],
                    'link': SOCCER_SUCK_TOPIC + '/' + entry["id"],
                    'publish_date': self._convert_datetime_to_epoch(entry['date'], SOCCER_SUCK_DATE_FORMAT),
                    'image_url': url
                }
            )
        data['entries'] = sorted(data['entries'], key=lambda k: k['publish_date'], reverse=True)
        return data

    def get_manutd_feed(self, limit):
        resp = session.get(MANUTD_RSS_FEED)
        data = dict()
        data['feed_title'] = resp.xml.xpath('//title', first=True).text
        data['feed_link'] = 'https://www.manutd.com/en/news/latest'
        data['feed_date'] = int(time())
        data['entries'] = []
        items = resp.xml.xpath('//item')
        for item in items:
            if len(data['entries']) > limit-1:
                break
            category = item.xpath('//category')[0].text
            if category.lower() == 'news':
                title = item.xpath('//title')[0].text
                if not title:
                    title = html2text.html2text(item.xpath('//newstext')[0].text)
                data['entries'].append(
                    {
                        'title': title,
                        'link': item.xpath('//link')[0].text,
                        'publish_date': self._convert_datetime_to_epoch(item.xpath('//pubDate')[0].text, UK_DATE_FORMAT),
                        'image_url': self._format_image_url(item.xpath('//image')[3].text)
                    }
                )
        return data

    def get_arsenal_feed(self, limit):
        d = feedparser.parse(ARSENAL_RSS_FEED)
        data = dict()
        data['feed_title'] = d.feed.title
        data['feed_link'] = d.feed.link
        data['feed_date'] = int(time())
        data['entries'] = []
        for index in range(0, limit):
            entry = d.entries[index]
            data['entries'].append(
                {
                    'title': entry['title'],
                    'link': entry['link'],
                    'publish_date': int(mktime(entry['published_parsed'])),
                    'image_url': entry['media_thumbnail'][0]['url']
                }
            )
        return data

    def get_liverpool_feed(self, limit):
        d = feedparser.parse(LIVERPOOL_RSS_FEED)
        data = dict()
        data['feed_title'] = d.feed.title
        data['feed_link'] = d.feed.link
        data['feed_date'] = time()
        data['entries'] = []
        for index in range(0, limit):
            entry = d.entries[index]
            data['entries'].append(
                {
                    'title': entry['title'],
                    'link': entry['link'],
                    'publish_date': mktime(entry['published_parsed']),
                    'image_url': entry['thumb']
                }
            )
        data['entries'] = sorted(data['entries'], key=lambda k: k['publish_date'], reverse=True)
        return data

    def get_chelsea_feed(self, limit):
        d = feedparser.parse(CHELSEA_RSS_FEED)
        data = dict()
        data['feed_title'] = d.feed.title
        data['feed_link'] = d.feed.link
        data['feed_date'] = int(time())
        data['entries'] = []
        for index in range(0, limit):
            entry = d.entries[index]
            data['entries'].append(
                {
                    'title': entry['title'],
                    'link': entry['link'],
                    'publish_date': int(mktime(entry['published_parsed'])),
                    'image_url': entry['media_thumbnail'][0]['url']
                }
            )
        return data

    def get_mancity_feed(self, limit):
        d = feedparser.parse(MANCITY_RSS_FEED)
        data = dict()
        data['feed_title'] = d.feed.title
        data['feed_link'] = d.feed.link
        data['feed_date'] = int(time())
        data['entries'] = []
        for index in range(0, limit):
            entry = d.entries[index]
            data['entries'].append(
                {
                    'title': entry['title'],
                    'link': entry['link'],
                    'publish_date': int(mktime(entry['published_parsed'])),
                    'image_url': entry['media_thumbnail'][0]['url']
                }
            )
        return data
    
    def get_live_feed(self):
        access_token = self._get_access_token()
        url = '{0}/fixtureschedule'.format(SOCCER_SUCK_API)
        body = {
            'access_token': access_token
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(url, headers=headers, data=body)
        return response.json()
    
    def create_live_flxed(self, data):
        for d in data:
            date = d['date']
            if self.is_today_in_thai(date):
                carousel_container = {
                    "type": "carousel",
                    "contents": []
                }
                for league in d['data']:
                    body = {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "text",
                                "text": "โปรแกรมถ่ายทอดสดฟุตบอล",
                                "size": "sm",
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": d['date'],
                                "size": "sm",
                                "align": "center"
                            }
                        ]
                    }
                    body['contents'].append(
                        {
                            "type": "text",
                            "text": league['match_title'],
                            "size": "xs",
                            "align": "center",
                            "weight": "bold",
                            "color": "#800000"
                        }
                    )
                    body['contents'].append(
                        {
                            "type": "separator",
                            "color": "#000000"
                        }
                    )
                    for match in league['data']:
                        if len(match['channel']) > 0:
                            body['contents'].append(
                                {
                                    "type": "box",
                                    "spacing": "sm",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "{0} {1} - {2}".format(match['time'], match['home_team'], match['away_team']),
                                            "flex": 0,
                                            "size": "xxs",
                                            "wrap": True
                                        },
                                        {
                                            "type": "text",
                                            "text": ','.join(match['channel']),
                                            "size": "xxs",
                                            "weight": "bold",
                                            "wrap": True,
                                            "color": "#008000"
                                        }
                                    ]
                                }
                            )
                        else:
                            body['contents'].append(
                                {
                                    "type": "text",
                                    "text": "{0} {1} - {2}".format(match['time'], match['home_team'], match['away_team']),
                                    "flex": 0,
                                    "size": "xxs",
                                    "wrap": True
                                }
                            )
                        body['contents'].append(
                            {
                                "type": "separator",
                                "color": "#000000"
                            }
                        )
                    bubble = {
                        "type": "bubble",
                        "body": body
                    }
                    carousel_container['contents'].append(bubble)
                return carousel_container

    def is_today_in_thai(self, date_str):
        date_obj = dateparser.parse(date_str, languages=['th'])
        today = dateparser.parse('today 00:00')
        today = today.replace(year=today.year + 543)
        return date_obj == today


if __name__ == '__main__':
    rss = RssFeed()
    print(rss.is_today_in_thai('วันเสาร์ที่ 2 มีนาคม 2562'))
