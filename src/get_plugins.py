import json
import os
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
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
from utils import convert_time


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
        # task_info.Progress.console.log(f"Fetching {max_length} plugins")
    for plugin in data:
        task_info.Progress.update(task_info.Task, description=f"Fetching {plugin.name}")
        plugin_manifest = manifest(plugin)
        plugin.isDesktopOnly = (
            plugin_manifest.isDesktopOnly
            if plugin_manifest.isDesktopOnly is not None
            else True
        )  # is None => Desktop Only plugin because too old
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
        if plugin.repo:
            owner = plugin.repo.split("/")[0]
            repo = plugin.repo.split("/")[1]
        else:
            raise Exception("No repo found")
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
            last_commit_date = convert_time(last_commit_date)
            etag = response.headers["ETag"].replace("W/", "")
    except Exception as e:
        print(e)
    return RepositoryInformationDate(last_commit_date=last_commit_date, etag=etag)


def save_plugin(plugins: list[PluginItems]) -> None:
    """
    Save the plugins in a json file
    """
    file_path = Path("plugins.json")
    with file_path.open("w", encoding="utf-8") as f:
        json.dump([x.model_dump() for x in plugins], f, ensure_ascii=False, indent=4)


def read_plugin_json(
    commit_date: list[EtagPlugins],
    task_info: Task_Info,
    max_length: Optional[int] = None,
) -> tuple[list[PluginItems], Task_Info]:
    """
    Read the json file and return a list of PluginItems
    """
    # get creation date of the json file

    file_path = Path("plugins.json")
    if file_path.exists():
        creation_date = file_path.stat().st_mtime
        now = datetime.now().timestamp()
        # if the file is older than 1 day, we update it
        if now - creation_date > 86400:  # noqa: PLR2004
            task_info.Progress.update(
                task_info.Task, description="File too old : Fetching new data"
            )
            plugins, task_info = get_raw_data(commit_date, task_info, max_length)
            save_plugin(plugins)
            return plugins, task_info
        else:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            # verify empty file
            if len(data) == 0:
                task_info.Progress.update(
                    task_info.Task, description="File is empty : Fetching new data"
                )
                plugins, task_info = get_raw_data(commit_date, task_info, max_length)
                save_plugin(plugins)
                return plugins, task_info
            else:
                task_info.Progress.update(
                    task_info.Task, description="File OK : Reading file"
                )
                plugins = [PluginItems(**x) for x in data]
                task_info.Progress.remove_task(task_info.Task)
                return plugins, task_info
    else:
        task_info.Progress.update(
            task_info.Task, description="File not found : Fetching new data"
        )
        plugins, task_info = get_raw_data(commit_date, task_info, max_length)
        save_plugin(plugins)
        return plugins, task_info
