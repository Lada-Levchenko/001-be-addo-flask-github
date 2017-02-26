from flask import Flask, render_template, request, abort
import jinja2
from client import GithubClient
import json
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/info", methods=['POST'])
def info():
    username = request.values.get('username', None)
    if not username:
        abort(400)
    variables = {'repo_table': get_repo_table(username), 'user_info': get_user_info(username), 'username': username}
    return render_template('index.html', **variables)


def get_repo_table(username):
    table = []
    repos_names = GithubClient.get_repos(username)
    for reponame in repos_names:
        commits = str(GithubClient.get_repo_commits(username, reponame))
        branches = str(GithubClient.get_repo_branches(username, reponame))
        table.append({'name': reponame, 'commits': commits, 'branches': branches})
    return table


def get_user_info(username):
    return GithubClient.get_user_info(username)


if __name__ == "__main__":
    app.run(debug=True)