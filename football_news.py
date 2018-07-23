import time

from linebot.models import (
    BubbleContainer
)

DATE_FORMAT = '%d %b %Y %H:%M:%S'


class FootballNews(object):

    def _convert_epoch_to_str(self, epoch):
        return time.strftime(DATE_FORMAT, time.localtime(epoch))

    def get_news_bubble(self, header_bg_color, data, header_text_color="#000000"):
        bubble = {
            "type": "bubble",
            "styles": {
                "header": {
                    "backgroundColor": header_bg_color
                }
            },
            "header": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                  {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "sm",
                    "contents": [
                      {
                        "type": "text",
                        "text": data["feed_title"],
                        "weight": "bold",
                        "color": header_text_color,
                        "size": "sm",
                        "wrap": True,
                        "action": {
                            "type": "uri",
                            "uri": data["feed_link"]
                        }
                      },
                      {
                        "type": "text",
                        "text": "Update: {0}".format(self._convert_epoch_to_str(data['feed_date'])),
                        "color": header_text_color,
                        "size": "xxs"
                      }
                    ]
                  }
                ]
            },
            "body": {
                "type": "box",
                "layout": "horizontal",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "md",
                        "contents": []
                    }
                ]
            }
        }
        for entry in data['entries']:
            body_contents = bubble["body"]["contents"][0]["contents"]
            body_contents.append(
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "image",
                            "url": entry["image_url"],
                            "aspectMode": "cover",
                            "aspectRatio": "4:3",
                            "margin": "md",
                            "size": "md",
                            "gravity": "top",
                            "flex": 1,
                            "action": {
                                "type": "uri",
                                "uri": entry["link"]
                            }
                        },
                        {
                            "type": "text",
                            "text": entry["title"],
                            "size": "xxs",
                            "wrap": True,
                            "flex": 2,
                            "action": {
                                "type": "uri",
                                "uri": entry["link"]
                            }
                        }
                    ]
                }
            )
            body_contents.append(
                {
                    "type": "separator"
                }
            )
        bubble_container = BubbleContainer.new_from_json_dict(bubble)
        return bubble_container