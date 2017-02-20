import pprint
import json
import requests
from requests import exceptions


def get_repos():
    try:
        response = requests.get('https://api.github.com/users/lionder/repos')
    except exceptions.InvalidSchema as e:
        print(e)
    else:
        print(response.status_code)
        print(response.content)
        print(response.json())
        pprint.pprint(response.json())
    finally:
        print("passed")


def create_repo():
    username = input('Username: ')
    password = input('Password: ')
    repodata = {'name': input('Repository Name: ')}
    try:
        response = requests.post('https://api.github.com/user/repos', auth=(username, password), data=json.dumps(repodata))

    except exceptions.InvalidSchema as e:
        print(e)
    else:
        print(response.status_code)
        print(response.content)
        print(response.json())
        pprint.pprint(response.json())
    finally:
        print("passed")


