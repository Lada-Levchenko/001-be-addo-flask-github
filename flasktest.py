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

@app.route("/repos", methods=['POST'])
def hello():
    username = request.values.get('username', None)
    if not username:
        abort(400)

    table = []
    repos_names = GithubClient.get_repos(username)
    for reponame in repos_names:
        commits = str(GithubClient.get_repo_commits(username, reponame))
        branches = str(GithubClient.get_repo_branches(username, reponame))
        table.append({'name': reponame, 'commits': commits, 'branches': branches})
    return render_template('index.html', **{'repo_table': table})

if __name__ == "__main__":
    app.run(debug=True)