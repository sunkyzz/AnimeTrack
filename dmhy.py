import requests
import xmltodict
from urllib.parse import unquote
from constant import logout


def get_magnets_from_query(keyword):
    def _get_hash_from_magnet(magnet):
        if magnet.find('magnet:?') == 0:
            hash_value = magnet.split(':')[3][:32]
            return hash_value

    url = unquote('http://share.dmhy.org/topics/rss/rss.xml?keyword={}'.format(keyword))
    r = requests.get(url)
    if r.ok:
        anime_dict = xmltodict.parse(r.content.decode('utf-8'))
    elif r.status_code == 523:
        logout("Oh, dmhy website is down now(HTTP 523). It can usually recover in a few hours.")
        return
    else:
        logout("RSS Access fail with keyword: {}, status code: {}, if it does not recover it a few days, replece issue in Github.".format(keyword, r.status_code))
        return

    if 'rss' in anime_dict and 'channel' in anime_dict['rss'] and 'item' in anime_dict['rss']['channel']:
        results = {}
        query_results = anime_dict['rss']['channel']['item']
        for query_result in query_results:
            if 'title' in query_result and 'enclosure' in query_result and '@url' in query_result['enclosure']:
                magnet = query_result['enclosure']['@url']
                hash_value = _get_hash_from_magnet(magnet)
                title = query_result['title']
                results[title] = (hash_value, magnet)
    return results
