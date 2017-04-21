import twitter
import requests
import simplejson

class youtube(object):
    key = '' #youtube dev api key

    def get_title(self, id):
        url = 'https://www.googleapis.com/youtube/v3/videos?part=snippet&id=%s&key=%s' % (id, self.key)
        page = requests.get(url)
        json = page.json()
        infor = json['items']
        for each in infor:
            title = each['snippet']['title']
            channelTitle = each['snippet']['channelTitle']

        return (title, channelTitle)


class twit_worm(object):
    api = twitter.Api(consumer_key='',
            consumer_secret='',
            access_token_key='',
            access_token_secret='')

    def get(self, statusid):
        status = self.api.GetStatus(statusid)
        stat = status.text
        user = status.user.name
        return (user, stat)
