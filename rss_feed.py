import feedparser
from datetime import datetime
from time import mktime, time
from bs4 import BeautifulSoup
import os
import ssl
import json
import re
import uuid
import requests

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

class RssFeed(object):

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
        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context
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
        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context
        d = feedparser.parse(MIRROR_RSS_FEED)
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
                    'publish_date': mktime(entry['published_parsed']),
                    'image_url': entry['media_content'][0]['url']
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
        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context
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
            r = requests.get(image_url)
            if r.status_code == 200:
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