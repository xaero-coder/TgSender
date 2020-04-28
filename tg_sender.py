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
            with open('tg_sender.conf', 'r') as config:
                conf = json.load(config)
                self.__users_dict = conf['USERS_DICT']
        except FileNotFoundError:
            number_of_users = int(input('please insert number of users: '))
            for _ in range(number_of_users):
                name = input('Name: ')
                user_id = int(input('ID: '))
                self.__users_dict[name] = user_id

    def __get_bot_token(self) -> str:
        self.__bot_token = ''
        try:
            with open('tg_sender.conf', 'r') as config:
                conf = json.load(config)
                return conf['BOT_TOKEN']
        except FileNotFoundError:
            self.__bot_token = input('hi, please insert your bot token: ')
            return self.__bot_token

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
                    for user in self.__get_users_id(self.__users_dict[receiver].keys()):
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
        except NameError:
            self.__http.request(url=url, method='POST', fields=data)

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
                requests.post(url=doc_url, data=data, files=files)
            except NameError:
                with open(file_path) as fp:
                    file_data = fp.read()
                    self.__http.request(url=doc_url, method='POST', fields={
                                        'document': (file_name, file_data), 'chat_id': user_id})

    def pull_doc(self) -> None:
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
            json_file = self.get_request(url=get_file_url, params=file_params)
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


sender = TgSender()


def interactive_menu():
    send_type = input('What do you want to send?(msg, file) ')
    recv = input('Who do you want to send it to?(example: admin, Tom, john) ')
    recv = recv.split(', ')
    if send_type == 'msg':
        message = input('Message: ')
        sender.send_message(message, recv)
    elif send_type == 'file':
        file = input('File_path: ')
        sender.send_file(file, recv)
    else:
        print('Bad input, try again...')
        interactive_menu()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        interactive_menu()
    else:
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
        else:
            print('-- Bad input --')