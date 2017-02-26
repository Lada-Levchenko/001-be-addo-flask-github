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
    api_url = "https://api.github.com"

    @staticmethod
    def get_repos(username):
        try:
            response = requests.get(GithubClient.api_url + '/users/%s/repos' % username)
        except exceptions.InvalidSchema as e:
            return e
        else:
            return [repo["name"] for repo in response.json()]

    @staticmethod
    def create_repo(username, password, reponame):
        repodata = {'name': reponame}
        try:
            response = requests.post(GithubClient.api_url + '/user/repos', auth=(username, password),
                                     data=json.dumps(repodata))
        except exceptions.InvalidSchema as e:
            return e
        else:
            return reponame + " created with id: " + str(response.json()['id'])

    @staticmethod
    def get_repo_info(username, reponame):
        try:
            response = requests.get(GithubClient.api_url + '/repos/%s/%s' % (username, reponame))
        except exceptions.InvalidSchema as e:
            return e
        else:
            info_dict = {}
            repo_obj = response.json()

            info_dict["total_commits"] = GithubClient.get_repo_commits(username, reponame)
            info_dict["branches"] = GithubClient.get_repo_branches(username, reponame)

            for param, value in repo_obj.items():
                if not isinstance(value, dict) and not param.endswith("_url"):
                    info_dict[param] = value

            return info_dict

    @staticmethod
    def get_repo_commits(username, reponame):
        try:
            response = requests.get(GithubClient.api_url + '/repos/%s/%s/stats/contributors' % (username, reponame))
        except exceptions.InvalidSchema as e:
            return e
        else:
            contributors = response.json()
            commits = 0
            if len(contributors) > 0:
                for contributor in contributors:
                    commits += contributor['total']
            return commits

    @staticmethod
    def get_repo_branches(username, reponame):
        try:
            response = requests.get(GithubClient.api_url + '/repos/%s/%s/branches' % (username, reponame))
        except exceptions.InvalidSchema as e:
            return e
        else:
            branches = response.json()
            return len(branches)

    @staticmethod
    def get_user_info(username):
        try:
            response = requests.get(GithubClient.api_url + '/users/%s' % username)
        except exceptions.InvalidSchema as e:
            return e
        else:
            info_obj = response.json()
            size = 0
            prevailing_language = "None"
            try:
                response2 = requests.get(info_obj['repos_url'])
            except exceptions.InvalidSchema as e:
                return e
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

            return [headers, data]


class Export(object):

    @staticmethod
    def create_dataset(data, headers_flag):
        if headers_flag:
            headers = data[0]
            del data[0]
            return tablib.Dataset(*data, headers=headers)
        else:
            return tablib.Dataset(*data)

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
        for key, value in repo_info.items():
            print(key + " = " + str(value))

    def do_export_user_info(self, arg):
        print("Export info about user:")
        username = input('Username: ')
        file_name = input("Choose name of exporting file: ")
        extension = input("Choose extension (for '.xls' type 0, for '.csv' type 1): ")
        print("Collecting info...")
        user_info = GithubClient.get_user_info(username)
        print("Info collected. Exporting...")
        if extension == '0':
            Export.export_to_xls(user_info, file_name, True)
        else:
            Export.export_to_csv(user_info, file_name, True)
        print("User Info exported!")

    def do_bye(self, arg):
        print('Thank you for using GithubClient')
        return True


if __name__ == "__main__":
    main()
