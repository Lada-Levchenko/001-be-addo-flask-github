import json
from nonstrict_mode import mode
import requests
from requests import exceptions
import getpass
import tablib
import cmd


def main():
    client = GithubClientShell()
    client.cmdloop(client.intro)


class GithubClient(object):

    @staticmethod
    def get_repos(username):
        try:
            response = requests.get('https://api.github.com/users/%s/repos' % username)
        except exceptions.InvalidSchema as e:
            return e.errno
        else:
            return [repo["name"] for repo in response.json()]

    @staticmethod
    def create_repo(username, password, reponame):
        repodata = {'name': reponame}
        try:
            response = requests.post('https://api.github.com/user/repos', auth=(username, password),
                                     data=json.dumps(repodata))
        except exceptions.InvalidSchema as e:
            return e.errno
        else:
            return reponame + " created with id: " + str(response.json()['id'])

    @staticmethod
    def get_repo_info(username, reponame):
        try:
            response = requests.get('https://api.github.com/repos/%s/%s' % (username, reponame))
        except exceptions.InvalidSchema as e:
            return e.errno
        else:
            info_list = []
            repo_obj = response.json()
            for param, value in repo_obj.items():
                if isinstance(value, dict):
                    info_list.append(param + " = complicated object")
                else:
                    info_list.append(param + " = " + str(value))
                    if param.endswith("_url") and value is not None and value != "https://github.com/%s/%s" % (
                            username, reponame) and not value.endswith(".git"):
                        try:
                            response2 = requests.get(value.split('{', 1)[0])
                        except (exceptions.InvalidSchema, exceptions.MissingSchema) as e:
                            return e.errno
                        else:
                            if type(response2.json()) is dict:
                                if 'message' in response2.json():
                                    info_list.append("....." + response2.json()['message'])
                                else:
                                    info_list.append(".....count: " + str(len(response2.json())))
            return info_list

    @staticmethod
    def get_user_info(username):
        try:
            response = requests.get('https://api.github.com/users/%s' % username)
        except exceptions.InvalidSchema as e:
            return e.errno
        else:
            info_obj = response.json()
            size = 0
            prevailing_language = "None"
            try:
                response2 = requests.get(info_obj['repos_url'])
            except exceptions.InvalidSchema as e:
                return e.errno
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

            return json.dumps([headers, data])


class Export(object):

    @staticmethod
    def create_dataset(data, headers_flag):
        rows = json.loads(data)
        if headers_flag:
            headers = rows[0]
            del rows[0]
            return tablib.Dataset(*rows, headers=headers)
        else:
            return tablib.Dataset(*rows)

    @staticmethod
    def export_to_xls(data, file_name, headers_flag=False):
        dataset = Export.create_dataset(data, headers_flag)
        return open(file_name + '.xls', 'wb').write(dataset.xls)

    @staticmethod
    def export_to_csv(data, file_name, headers_flag=False):
        dataset = Export.create_dataset(data, headers_flag)
        return open(file_name + '.csv', 'w').write(dataset.csv)


class GithubClientShell(cmd.Cmd):
    intro = 'Welcome to the GithubClient shell.   Type help or ? to list commands.\n'
    prompt = '(GithubClient) '

    def do_get_repos(self, arg):
        print("Get all repositories of user:")
        username = input('Username: ')
        repo_names = GithubClient.get_repos(username)
        print("Repositories: ")
        for name in repo_names:
            print(name)

    def do_create_repo(self, arg):
        print("Create new repository:")
        username = input('Username: ')
        password = getpass.getpass('Password: ')
        reponame = input('Repository Name: ')
        message = GithubClient.create_repo(username, password, reponame)
        print(message)

    def do_get_repo_info(self, arg):
        print("Get info about user's repository:")
        username = input('Username: ')
        reponame = input('Repository Name: ')
        print("Collecting info...")
        repo_info = GithubClient.get_repo_info(username, reponame)
        print("Repository Info: ")
        for line in repo_info:
            print(line)

    def do_export_user_info(self, arg):
        print("Export info about user:")
        username = input('Username: ')
        file_name = input("Choose name of exporting file: ")
        extension = input("Choose extension (for '.xls' type 0, for '.csv' type 1): ")
        print("Collecting info...")
        user_info = GithubClient.get_user_info(username)
        print("Info collected. Exporting...")
        if extension == '0':
            Export.export_to_xls(user_info, file_name)
        else:
            Export.export_to_csv(user_info, file_name)
        print("User Info exported!")

    def do_bye(self, arg):
        print('Thank you for using GithubClient')
        return True


if __name__ == "__main__":
    main()
