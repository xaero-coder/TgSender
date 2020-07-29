#! /bin/pyhton3

import json
import sys

try:
    import requests
except ImportError:
    import urllib3
    import urllib.request


class TgSender:
    def __init__(self):
        self.__bot_url = f'https://api.telegram.org/bot{self.__get_bot_token()}/'
        self.__set_users_dict()
        try:
            self.__http = urllib3.PoolManager()
        except NameError:
            pass

    def __set_users_dict(self) -> None:
        self.__users_dict = {}
        try:
            with open('config.json', 'r') as conf:
                config = json.load(conf)
                self.__users_dict = config['USERS_DICT']
        except FileNotFoundError:
            init()
            # self.__users_dict = {
            #     'admin': 1234567,
            #     'admin2': 1234567,
            #     'operator': ['admin1', 'admin2']
            # }

    def __get_bot_token(self) -> str:
        self.__bot_token = ''
        try:
            with open('config.json', 'r') as conf:
                config = json.load(conf)
                return config['BOT_TOKEN']
        except FileNotFoundError:
            init()
            # bot_token = ''
            # return bot_token

    def __get_users_id(self, receivers) -> list:
        """
        :param receivers:
        :type receivers: list[str]
        """
        users_id = []
        for receiver in receivers:
            try:
                if type(self.__users_dict[receiver]) == int:
                    users_id.append(self.__users_dict[receiver])
                else:
                    for user in self.__get_users_id(self.__users_dict[receiver]):
                        users_id.append(user)
            except KeyError:
                print(f'user "{receiver}" not found!')
        users_id = list(dict.fromkeys(users_id))
        return users_id

    def post_request(self, url, data) -> None:
        """
        :param url:
        :type url: str
        :param data:
        :type data: dict
        """
        try:
            requests.post(url=url, data=data)
        except NameError as ex:
            self.__http.request(url=url, method='POST', fields=data)
            print(ex)

    def get_request(self, url, params) -> dict:
        """
        :param url:
        :type url: str
        :param params:
        :type params: dict
        """
        try:
            update_req = requests.get(url=url, params=params)
            json_file = update_req.json()
        except NameError:
            update_req = self.__http.request(
                url=url, method='GET', fields=params)
            json_file = json.loads(update_req.data.decode('utf-8'))
        return json_file

    def send_message(self, message, receivers) -> None:
        """
        :param message:
        :type message: str
        :param receivers:
        :type receivers: list[str]
        """
        users_id = self.__get_users_id(receivers)
        message_url = self.__bot_url + 'sendMessage'
        for user_id in users_id:
            data = {
                'chat_id': user_id,
                'text': message
            }
            self.post_request(url=message_url, data=data)

    def send_file(self, file_path, receivers) -> None:
        """
        :param file_path:
        :type file_path: str
        :param receivers:
        :type receivers: list[str]
        """
        try:
            file_name = file_path.split('/')[-1]
            users_id = self.__get_users_id(receivers)
            doc_url = self.__bot_url + 'sendDocument'
            for user_id in users_id:
                data = {
                    'chat_id': user_id,
                }
                files = {
                    'document': open(file_path, 'rb')
                }
                try:
                    res = requests.post(url=doc_url, data=data, files=files)
                    if not res.json()['ok']:
                        raise Exception(res.json()['Request Entity Too Large'])
                except NameError:
                    with open(file_path) as fp:
                        file_data = fp.read()
                        self.__http.request(url=doc_url, method='POST', fields={
                            'document': (file_name, file_data), 'chat_id': user_id})
        except Exception as ex:
            print(ex)
            raise ex

    def pull_doc(self) -> None:
        try:
            push_url = self.__bot_url + 'getUpdates'
            update_params = {
                'offset': -1,
            }
            json_file = self.get_request(url=push_url, params=update_params)
            file_name = json_file['result'][0]['message']['document']['file_name']
            username = json_file['result'][0]['message']['from']['username']
            inp = input(f'get file "{file_name}" from <<@{username}>>?[Y/n] ')
            if inp in ['', 'Y', 'yes', 'y']:
                print('downloading...')
                try:
                    file_id = json_file['result'][0]['message']['document']['file_id']
                except KeyError:
                    file_id = json_file['result'][0]['message']['document']['thumb']['file_id']
                file_params = {
                    'file_id': file_id
                }
                get_file_url = f'https://api.telegram.org/bot{self.__get_bot_token()}/getFile'
                json_file = self.get_request(
                    url=get_file_url, params=file_params)
                get_file_path = json_file['result']['file_path']
                file_url = f'https://api.telegram.org/file/bot{self.__get_bot_token()}/{get_file_path}'
                with open(file_name, 'wb') as fd:
                    try:
                        get_file_req = requests.get(url=file_url)
                        for chunk in get_file_req.iter_content(chunk_size=512 * 1024):
                            if chunk:
                                fd.write(chunk)
                    except NameError:
                        urllib.request.urlretrieve(
                            url=file_url, filename=file_name)
                print('download completed')
            else:
                print('download canceled by you!')
        except IndexError as ie:
            print(ie)
            print('Maybe No File To Download...')
            raise ie
        except KeyError as ke:
            print(ke)
            print('Maybe Request Entity Too Large')
            raise ke
        except Exception as ex:
            print(ex)
            raise ex


def init():
    bot_token = input('Hi, please insert your bot token:\n')
    number_of_users = int(input('please insert number of users:\n'))
    data = {'USERS_DICT': {}, 'BOT_TOKEN': bot_token}
    for _ in range(number_of_users):
        name = input('Name: ')
        user_id = int(input('ID: '))
        data['USERS_DICT'].update({name: user_id})
    with open('config.json', 'w') as conf:
        json.dump(data, conf, indent=4)


def menu():
    if len(sys.argv) not in [1, 2, 4]:
        raise Exception('-- Bad Input --')
    if len(sys.argv) == 2 and sys.argv[-1] == 'init':
        init()
    else:
        if sys.argv[1] not in ['msg', 'file', 'pull']:
            raise Exception('-- Bad Input --')
        sender = TgSender()
        if sys.argv[1] == 'msg':
            msg = sys.argv[-2]
            msg_receivers = sys.argv[-1].split(', ')
            sender.send_message(message=msg, receivers=msg_receivers)
        elif sys.argv[1] == 'file':
            doc_path = sys.argv[-2]
            file_receivers = sys.argv[-1].split(', ')
            sender.send_file(file_path=doc_path, receivers=file_receivers)
        elif sys.argv[1] == 'pull':
            sender.pull_doc()


if __name__ == '__main__':
    menu()
