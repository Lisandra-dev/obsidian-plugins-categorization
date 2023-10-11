import json
import os
import urllib.error
import urllib.request
from typing import Optional

import requests
from interface import (
    EtagPlugins,
    Manifest,
    PluginItems,
    RepositoryInformationDate,
    Task_Info,
    UnDate,
    UnString,
)


def manifest(plugin: PluginItems) -> Manifest:
    try:
        with urllib.request.urlopen(
            f"https://raw.githubusercontent.com/{plugin.repo}/master/manifest.json"
        ) as url:
            manifest = json.loads(url.read().decode())
            return Manifest(**manifest)
    except urllib.error.HTTPError:
        with urllib.request.urlopen(
            f"https://raw.githubusercontent.com/{plugin.repo}/main/manifest.json"
        ) as url:
            manifest = json.loads(url.read().decode())
            return Manifest(**manifest)


def get_raw_data(
    commit_date: list[EtagPlugins],
    task_info: Task_Info,
    max_length: Optional[int] = None,
) -> tuple[list[PluginItems], Task_Info]:
    url = "https://raw.githubusercontent.com/obsidianmd/obsidian-releases/master/community-plugins.json"
    content = urllib.request.urlopen(url).read()
    data: list[PluginItems] = [PluginItems(**x) for x in json.loads(content)]
    if max_length:
        data = data[:max_length]
    for plugin in data:
        plugin_manifest = manifest(plugin)
        plugin.isDesktopOnly = plugin_manifest.isDesktopOnly
        plugin.fundingUrl = first_funding_url(plugin_manifest)
        db_plugin_date = [x for x in commit_date if x.plugin_id == plugin.id]
        etag = None
        last_commit_date = None
        task_info.Progress.update(task_info.Task, advance=0.5)
        if len(db_plugin_date) > 0:
            db_plugin_date = db_plugin_date[0]
            etag = db_plugin_date.etag
            last_commit_date = db_plugin_date.commit_date
        repo_info = get_repository_information(
            plugin, etag, last_commit_date=last_commit_date
        )
        task_info.Progress.update(task_info.Task, advance=0.5)
        plugin.last_commit_date = repo_info.last_commit_date
        plugin.etag = repo_info.etag
    return data, task_info


def first_funding_url(plugin: Manifest) -> str:
    # in the manifest the fundingUrl can be a list of dict or a str
    # we only want the first one
    if isinstance(plugin.fundingUrl, str):
        return plugin.fundingUrl
    elif isinstance(plugin.fundingUrl, list):
        return plugin.fundingUrl[0]["url"]
    else:
        return ""


def get_repository_information(
    plugin: PluginItems,
    etag: UnString = None,
    last_commit_date: UnDate = None,
) -> RepositoryInformationDate:
    try:
        # call the commits info using octokit + the etag from the database
        # if the etag is not None
        # no support for etag in GithubPy, use request as fallback
        owner = plugin.repo.split("/")[0]
        repo = plugin.repo.split("/")[1]
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        header = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {os.getenv("GITHUB_TOKEN")}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if etag:
            header["If-None-Match"] = etag
        response = requests.get(url, headers=header)
        if response.status_code == 200:  # noqa: PLR2004
            data = response.json()
            last_commit_date = data[0]["commit"]["author"]["date"]
            etag = response.headers["ETag"].replace("W/", "")
    except Exception as e:
        print(e)
    return RepositoryInformationDate(last_commit_date=last_commit_date, etag=etag)
