from dmhy import get_magnets_from_query, rpc_torrent
from constant import anime_config_path, magnet_config_path, check_frequence, logout, aria2_config_path, tracker_url
import os
import csv
import time
import requests
import argparse

support_website = ('dmhy')


class LoadConfig(object):
    def _try_create_empty_file(self, path):
        # try create config file
        try:
            open(path, 'a').close()
            logout('File {} not found, created empty one for you ;)'.format(path))
        except Exception as e:
            raise Exception("Create file {} fail: {}, maybe you need to create it manually.".format(path, e))
            exit()

    def _validate_path(self, path):
        if not os.path.exists(path):
            print('Path not exist in keyword file, path: {}, will try to create it.'.format(anime_config_path, path))
            try:
                os.mkdir(path)
                print('Create Path Success, Path: {}.'.format(path))
                return True
            except Exception as e:
                print('Create Path Fail, Path: {} Error:{}'.format(path, e))
                return False
        return True

    def _validate_anime_config_path(self, anime_config_path):
        if not os.path.exists(anime_config_path):
            self._try_create_empty_file(anime_config_path)

    def _validate_magnet_file(self, config_path):
        config_path = os.path.abspath(config_path)
        if not os.path.exists(config_path):
            self._try_create_empty_file(config_path)

    def load_anime_config_path(self, anime_config_path):
        anime_config_path = os.path.abspath(anime_config_path)
        self._validate_anime_config_path(anime_config_path)
        # load anime csv
        with open(anime_config_path, 'r', newline='', encoding='utf-8', errors='ignore') as csv2:
            rows = csv.reader(csv2)
            anime_config = {}
            for row in rows:
                # check len
                if len(row) < 2:
                    print('Invaild row: {} has been pass.'.format(str(row)))
                    continue
                # add website
                elif len(row) == 2:
                    website = 'dmhy'
                else:
                    website = row[2].replace(' ', '')
                # check website
                if website not in support_website:
                    print('Invaild website: {}, the row [{}] has been pass.'.format(str(website), row))
                    continue

                keyword = row[0].replace(' ', '+')
                path = os.path.abspath(row[1])
                # validate path
                if self._validate_path(path):
                    anime_config[keyword] = (path, website)
        # check config content empty
        if not anime_config:
            print('Empty anime config: {}, you can add your config follow example file.'.format(anime_config_path))
            exit()
        return anime_config

    def load_magnet_config(self, magnet_config_path):
        magnet_config_path = os.path.abspath(magnet_config_path)
        self._validate_magnet_file(magnet_config_path)
        result = []
        with open(magnet_config_path, 'r', encoding='utf-8', errors='ignore') as magnet_config:
            for magnet in magnet_config:
                result.append(magnet.replace('\n', ''))
        return result


def check_anime(anime_config, magnets, download=True):
    # check query urls in anime csv
    for keyword, keys in anime_config.items():
        path = keys[0]
        # TODO: Support more websites.
        website = keys[1]
        # get query magnets and hash value
        # query_magnets {title: (hash_value, magnet)}
        query_magnets = get_magnets_from_query(keyword)
        if not query_magnets:
            return
        for title, magnet_info in query_magnets.items():
            hash_value, magnet = magnet_info[0], magnet_info[1]
            if hash_value not in magnets:
                if download:
                    # rpc download
                    rpc_torrent(magnet, hash_value, path)

                # update magnet config
                with open(os.path.abspath(magnet_config_path), 'a', encoding='utf-8', errors='ignore') as magnet_config:
                    magnet_config.write('{}\n'.format(hash_value))

                logout("=" * 50)
                logout('[{}] \n    New Anime found:{}'.format(
                    time.strftime('%y/%m/%d %A %H:%M:%S', time.localtime(time.time())),
                    title))


def update_aria_trackers(url=tracker_url):
    aria_config = os.path.abspath(aria2_config_path)
    if not os.path.exists(aria_config):
        print('Aria2 Config {} not exist, please check constants/aria2_config_path'.format(aria_config))
        return
    r = requests.get(url)
    if r.ok:
        trackers = 'bt-tracker=' + r.content.decode('utf-8').replace('\n\n', '\n').replace('\n', ',')
        # load file
        if os.path.exists(aria_config):
            with open(aria_config, 'r', encoding='utf-8', errors='ignore') as conf:
                conf_str = ''
                for n in conf:
                    if n.find('bt-tracker=') == -1:
                        conf_str += n
                conf_str += trackers
            with open(aria_config, 'w', encoding='utf-8', errors='ignore') as conf:
                conf.write(conf_str)
        logout('[{}] aria2 config trackers update success.'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
    else:
        logout('trackers update url not reachable. please check constants/tracker_url')


def main(update_trackers=True, download=True, loop_check=True):
    logout('=' * 50)
    if update_trackers:
        try:
            logout('Start to update trackers')
            update_aria_trackers()
        except Exception as e:
            logout('trackers update fail, error: {}, you can manually update it in aria2.conf'.format(e))
    while True:
        try:
            # anime_config: keyword, path
            anime_config = LoadConfig().load_anime_config_path(anime_config_path)
            magnets = LoadConfig().load_magnet_config(magnet_config_path)
            check_anime(anime_config, magnets, download=download)
        except Exception as e:
            logout('[{}]\n    anime check fail, error: {}'.format(
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                e))
        if not loop_check:
            exit()
        logout('[{}] Anime track is running, Next check time: {}\r'.format(
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + check_frequence))), end='', flush=True)

        time.sleep(check_frequence)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Otaku Track', usage='', description='Track anime update in magnet website.')
    parser.add_argument('-f', help='only add to magnets.txt, do not download.', action='store_false')
    parser.add_argument('-t', help='update aria2.conf trackers.', action='store_true')
    parser.add_argument('-o', help='Only check once.', action='store_false')
    args = parser.parse_args()

    update_trackers_flag = args.t
    download = args.f
    loop_check = args.o

    main(update_trackers=update_trackers_flag, download=download, loop_check=loop_check)
