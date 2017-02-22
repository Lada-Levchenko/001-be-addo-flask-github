import json
from statistics import mode
import requests
from requests import exceptions
import getpass
import tablib


def get_repos():
    print("Get all repositories of user:")
    username = input('Username: ')
    try:
        response = requests.get('https://api.github.com/users/%s/repos' % username)
    except exceptions.InvalidSchema as e:
        print(e)
    else:
        print(response.status_code)
        print("Repositories:")
        [print(repo["name"]) for repo in response.json()]
    finally:
        print("get_repos finished!")


def create_repo():
    print("Create new repository:")
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
        print("Repositories:")
        [print(repo["name"]) for repo in response.json()]
    finally:
        print("create_repo finished!")


def get_repo_info():
    print("Get info about user's repository:")
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
                if param.endswith("_url") and value is not None and value != "https://github.com/%s/%s" % (
                username, repo) and not value.endswith(".git"):
                    try:
                        response2 = requests.get(value.split('{', 1)[0])
                    except (exceptions.InvalidSchema, exceptions.MissingSchema) as e:
                        print(e)
                    else:
                        if type(response2.json()) is dict:
                            print(".....count: " + str(len(response2.json())))
            else:
                print(param + " = complicated object")
    finally:
        print("get_repo_info finished!")


def export_user_info():
    print("Export info about user:")
    username = input('Username: ')
    try:
        response = requests.get('https://api.github.com/users/%s' % username)
    except exceptions.InvalidSchema as e:
        print(e)
    else:
        print(response.status_code)
        info_obj = response.json()

        size = 0
        prevailing_language = "None"
        try:
            response2 = requests.get(info_obj['repos_url'])
        except exceptions.InvalidSchema as e:
            print(e)
        else:
            languages = []
            for repo in response2.json():
                size += repo['size']
                if repo['language'] is not None:
                    languages.append(repo['language'])
            size /= 1024
            prevailing_language = mode(languages)

        headers = ('login', 'public_repos', 'prevailing_language', 'updated_at', 'size (MB)', 'followers')
        data = (info_obj['login'],
                info_obj['public_repos'],
                prevailing_language,
                info_obj['updated_at'],
                size,
                info_obj['followers'])
        dataset = tablib.Dataset(data, headers=headers)

        file_name = input("Choose name of exporting file: ")
        answer = input("Choose extension (for '.xls' type 0, for '.csv' type 1): ")
        extension = '.xls' if answer == '0' else '.csv'
        final_set = dataset.xls if answer == '0' else dataset.csv
        method = 'wb' if answer == '0' else 'w'
        open(file_name + extension, method).write(final_set)
    finally:
        print("export_user_info finished!")



