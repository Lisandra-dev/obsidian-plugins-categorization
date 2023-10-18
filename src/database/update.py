import os
from typing import Any

import pandas as pd
import requests
from interface import PluginItems, PluginProperties, State, Task_Info
from seatable_api import Base
from utils import convert_time, generate_activity_tag

from database.search import get_plugin_in_database

from .automatic_category import add_new_keywords, new_keywords_list, update_links


def update(  # noqa
    plugin: PluginItems,
    database: pd.DataFrame,
    seatable: Base,
    task_info: Task_Info,
    keywords: pd.DataFrame,
    link_id: str,
    archive: bool = False,
) -> None:
    db = get_plugin_in_database(database, plugin).iloc[0]
    plugin_in_db = PluginItems(
        id=str(db["ID"]),
        name=str(db["Name"]),
        description=str(db["Description"]),
        repo=str(db["Github Link"].replace("https://github.com/", ""))
        if db["Github Link"]
        else None,
        author=str(db["Author"]) if db["Author"] else None,
        fundingUrl=str(db["Funding URL"]) if db["Funding URL"] else None,
        isDesktopOnly=not bool(db["Mobile friendly"])
        if db["Mobile friendly"]
        else None,
        last_commit_date=db["Last Commit Date"] if db["Last Commit Date"] else None,
        etag=str(db["ETAG"]) if db["ETAG"] else None,
        status=State(db["Status"]) if db["Status"] else None,
    )
    error = bool(db["Error"]) if db["Error"] else False
    console = task_info.Progress.console
    database_properties = {
        "ID": plugin_in_db.id,
        "Name": plugin_in_db.name,
        "Description": plugin_in_db.description,
        "Github Link": f"https://github.com/{plugin_in_db.repo}",
        "Author": plugin_in_db.author,
        "Funding URL": plugin_in_db.fundingUrl,
        "Mobile friendly": plugin_in_db.isDesktopOnly,
        "Last Commit Date": plugin_in_db.last_commit_date,
        "ETAG": plugin_in_db.etag,
        "Status": str(plugin_in_db.status),
        "Error": error,
        "Plugin Available": bool(db["Plugin Available"])
        if db["Plugin Available"]
        else True,
        "Auto-Suggested Categories": db["Auto-Suggested Categories"]
        if db["Auto-Suggested Categories"]
        else None,
    }

    plugin_properties = PluginProperties(
        database_properties=database_properties,
        plugin=plugin,
        seatable=plugin_in_db,
        console=console,
    )
    must_update = []
    must_update, database_properties = update_author(plugin_properties, must_update)
    must_update, database_properties = update_description(
        plugin_properties, must_update
    )
    must_update, database_properties = update_funding(plugin_properties, must_update)
    must_update, database_properties = update_desktop_only(
        plugin_properties, error=error, must_update=must_update
    )
    must_update, database_properties = update_last_date(plugin_properties, must_update)
    must_update, database_properties = update_etag(plugin_properties, must_update)
    must_update, database_properties = update_status(plugin_properties, must_update)
    must_update, database_properties = plugin_repo(plugin_properties, must_update)
    if archive:
        must_update, database_properties = update_archived(
            plugin_properties, must_update
        )
    to_update = update_keywords(
        plugin_properties=plugin_properties,
        keywords=keywords,
        auto_suggest_in_database=db["Auto-Suggested Categories"],
        seatable=seatable,
        id=(link_id, db["_id"]),
    )
    must_update.append(to_update)
    if any(must_update):
        console.log(f"Updating {plugin_in_db.name}")
        seatable.update_row("Plugins", db["_id"], database_properties)
    task_info.Progress.update(task_info.Task, advance=1)


def update_desktop_only(
    plugin_properties: PluginProperties,
    error: bool,
    must_update: list[bool],
) -> tuple[list[bool], dict[str, Any]]:
    to_update = False
    database_properties, plugin, plugin_in_db, console = [
        plugin_properties.database_properties,
        plugin_properties.plugin,
        plugin_properties.seatable,
        plugin_properties.console,
    ]
    if (plugin_in_db.isDesktopOnly != plugin.isDesktopOnly) and not error:
        console.log(
            f"[italic red]Mismatched isDesktopOnly: {plugin_in_db.isDesktopOnly} != {not(plugin.isDesktopOnly)}"
        )
        # not that the value is invert; if the plugin is mobile friendly, the value is False
        to_update = True
        database_properties["Mobile friendly"] = not plugin.isDesktopOnly
    must_update.append(to_update)
    return (must_update, database_properties)


def update_author(
    plugin_info: PluginProperties, must_update: list[bool]
) -> tuple[list[bool], dict[str, Any]]:
    to_update = False
    database_property, plugin, plugin_in_db, console = [
        plugin_info.database_properties,
        plugin_info.plugin,
        plugin_info.seatable,
        plugin_info.console,
    ]

    if plugin_in_db.author != plugin.author:
        console.log(
            f"[italic red]Mismatched author: {plugin_in_db.author} != {plugin.author}"
        )
        to_update = True
        database_property["Author"] = plugin.author
    must_update.append(to_update)
    return (must_update, database_property)


def update_description(
    plugin_info: PluginProperties, must_update: list[bool]
) -> tuple[list[bool], dict[str, Any]]:
    to_update = False
    database_property, plugin, plugin_in_db, console = [
        plugin_info.database_properties,
        plugin_info.plugin,
        plugin_info.seatable,
        plugin_info.console,
    ]

    if (plugin_in_db.description != plugin.description) and plugin.description:
        console.log(
            f"[italic red]Mismatched description: {plugin_in_db.description} != {plugin.description}"
        )
        to_update = True
        database_property["Description"] = plugin.description
    must_update.append(to_update)
    return (must_update, database_property)


def update_funding(
    plugin_info: PluginProperties, must_update: list[bool]
) -> tuple[list[bool], dict[str, Any]]:
    to_update = False
    database_property, plugin, plugin_in_db, console = [
        plugin_info.database_properties,
        plugin_info.plugin,
        plugin_info.seatable,
        plugin_info.console,
    ]

    if (plugin_in_db.fundingUrl != plugin.fundingUrl) and plugin.fundingUrl:
        console.log(
            f"[italic red]Mismatched fundingUrl: {plugin_in_db.fundingUrl} != {plugin.fundingUrl}"
        )
        to_update = True
        database_property["Funding URL"] = plugin.fundingUrl
    must_update.append(to_update)
    return (must_update, database_property)


def update_last_date(
    plugin_info: PluginProperties, must_update: list[bool]
) -> tuple[list[bool], dict[str, Any]]:
    to_update = False
    database_property, plugin, plugin_in_db, console = [
        plugin_info.database_properties,
        plugin_info.plugin,
        plugin_info.seatable,
        plugin_info.console,
    ]

    plugin.last_commit_date = convert_time(plugin.last_commit_date)
    plugin_in_db.last_commit_date = convert_time(plugin_in_db.last_commit_date)

    if plugin_in_db.last_commit_date != plugin.last_commit_date:
        console.log(
            f"[italic red]Mismatched last_commit_date: {plugin_in_db.last_commit_date} != {plugin.last_commit_date}"
        )
        to_update = True
        database_property["Last Commit Date"] = plugin.last_commit_date
    must_update.append(to_update)
    return (must_update, database_property)


def update_etag(
    plugin_info: PluginProperties, must_update: list[bool]
) -> tuple[list[bool], dict[str, Any]]:
    to_update = False
    database_property, plugin, plugin_in_db, console = [
        plugin_info.database_properties,
        plugin_info.plugin,
        plugin_info.seatable,
        plugin_info.console,
    ]

    if plugin_in_db.etag != plugin.etag:
        console.log(
            f"[italic red]Mismatched etag: {plugin_in_db.etag} != {plugin.etag}"
        )
        to_update = True
        database_property["ETAG"] = plugin.etag
    must_update.append(to_update)
    return (must_update, database_property)


def update_status(
    plugin_info: PluginProperties, must_update: list[bool]
) -> tuple[list[bool], dict[str, Any]]:
    to_update = False
    database_property, plugin, plugin_in_db, console = [
        plugin_info.database_properties,
        plugin_info.plugin,
        plugin_info.seatable,
        plugin_info.console,
    ]

    status = generate_activity_tag(plugin)

    if (plugin_in_db.status != status) and plugin_in_db.status not in [
        State.ARCHIVED,
        State.MAINTENANCE,
    ]:
        console.log(f"[italic red]Mismatched status: {plugin_in_db.status} != {status}")
        to_update = True
        database_property["Status"] = str(status)
    must_update.append(to_update)
    return (must_update, database_property)


def plugin_repo(
    plugin_info: PluginProperties, must_update: list[bool]
) -> tuple[list[bool], dict[str, Any]]:
    to_update = False
    database_property, plugin, plugin_in_db, console = [
        plugin_info.database_properties,
        plugin_info.plugin,
        plugin_info.seatable,
        plugin_info.console,
    ]

    if (plugin_in_db.repo != plugin.repo) and plugin.repo:
        console.log(
            f"[italic red]Mismatched repo: {plugin_in_db.repo} != {plugin.repo}"
        )
        to_update = True
        database_property["Github Link"] = f"https://github.com/{plugin.repo}"
    must_update.append(to_update)
    return (must_update, database_property)


def update_keywords(
    plugin_properties: PluginProperties,
    keywords: pd.DataFrame,
    auto_suggest_in_database: list[Any],
    seatable: Base,
    id: tuple[str, str],
) -> bool:
    database_property, plugin, console = [
        plugin_properties.database_properties,
        plugin_properties.plugin,
        plugin_properties.console,
    ]
    to_update = False
    auto_category: list[Any] = add_new_keywords(database_property, plugin, keywords)
    keywords_list: list[Any] = new_keywords_list(database_property, auto_category)

    if keywords_list != auto_suggest_in_database:
        console.log(
            f"[italic red]Mismatched auto-suggested categories : {auto_category} != {auto_suggest_in_database}"
        )
        link_id, row_id = id
        update_links(seatable, link_id, auto_category, row_id)
        to_update = True
    return to_update


def update_archived(
    plugin_info: PluginProperties, must_update: list[bool]
) -> tuple[list[bool], dict[str, Any]]:
    to_update = False
    database_property, plugin, plugin_in_db, console = [
        plugin_info.database_properties,
        plugin_info.plugin,
        plugin_info.seatable,
        plugin_info.console,
    ]
    console.log("Triggered archive update")

    # get archived state from Github API
    if plugin.repo:
        owner = plugin.repo.split("/")[0]
        repo = plugin.repo.split("/")[1]
    else:
        raise Exception("No repo found")
    url = f"https://api.github.com/repos/{owner}/{repo}"
    header = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {os.getenv("GITHUB_TOKEN")}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    response = requests.get(url, headers=header)
    if response.status_code == 200:  # noqa: PLR2004
        data = response.json()
        if data["archived"] and plugin_in_db.status != State.ARCHIVED:
            console.log(f"[italic red]Archived: {plugin_in_db.name}")
            to_update = True
            database_property["Status"] = str(State.ARCHIVED)
    must_update.append(to_update)
    return (must_update, database_property)
