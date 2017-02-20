import pprint
import json
import requests
from requests import exceptions
import getpass


def get_repos():
    try:
        response = requests.get('https://api.github.com/users/lionder/repos')
    except exceptions.InvalidSchema as e:
        print(e)
    else:
        print(response.status_code)
        print(response.content)
        pprint.pprint(response.json())
    finally:
        print("get_repos finished!")


def create_repo():
    username = input('Username: ')
    password = getpass.getpass('Password: ')
    repodata = {'name': input('Repository Name: ')}
    try:
        response = requests.post('https://api.github.com/user/repos', auth=(username, password),
                                 data=json.dumps(repodata))

    except exceptions.InvalidSchema as e:
        print(e)
    else:
        print(response.status_code)
        print(response.content)
        pprint.pprint(response.json())
    finally:
        print("create_repo finished!")


def get_repo_info():
    username = input('Username: ')
    repo = input('Repository Name: ')
    try:
        response = requests.get('https://api.github.com/repos/%s/%s' % (username, repo))
    except exceptions.InvalidSchema as e:
        print(e)
    else:
        print(response.status_code)
        repo_obj = response.json()
        for param, value in repo_obj.items():
            if not isinstance(value, dict):
                print(param + " = " + str(value))
            else:
                print(param + " = complicated object")
            if param.endswith("_url") and value is not None and value != "https://github.com/%s/%s" % (username, repo) and not value.endswith(".git"):
                try:
                    response2 = requests.get(value)
                except (exceptions.InvalidSchema, exceptions.MissingSchema) as e:
                    print(e)
                else:
                    print(".....count: " + str(len(response2.json())))
    finally:
        print("get_repo_info finished!")


get_repo_info()
