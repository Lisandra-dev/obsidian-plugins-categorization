from datetime import datetime

import pandas as pd
from interface import PluginItems, State, Task_Info
from seatable_api import Base
from utils import generate_activity_tag

from database.search import get_plugin_in_database


def update_old_entry(
    plugin: PluginItems,
    database: pd.DataFrame,
    seatable: Base,
    track_info: Task_Info,
) -> None:
    console = track_info.Progress.console
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

    database_properties = {
        "ID": plugin_in_db.id,
        "Name": plugin_in_db.name,
        "Description": plugin_in_db.description,
        "Github Link": f"https://github.com/{plugin_in_db.repo}",
        "Author": plugin_in_db.author,
        "Funding URL": plugin_in_db.fundingUrl,
        "Mobile friendly": not plugin_in_db.isDesktopOnly,
        "Last Commit Date": plugin_in_db.last_commit_date,
        "ETAG": plugin_in_db.etag,
        "Status": plugin_in_db.status,
        "Error": error,
        "Plugin Available": bool(db["Plugin Available"])
        if db["Plugin Available"]
        else True,
    }
    to_update = False
    # check if the plugin has changed
    if (plugin_in_db.author != plugin.author) and plugin.author:
        console.log(
            f"[italic red]Mismatched author: {plugin_in_db.author} != {plugin.author}"
        )
        to_update = True
        database_properties["Author"] = plugin.author

    if (plugin_in_db.description != plugin.description) and plugin.description:
        console.log(
            f"[italic red]Mismatched description: {plugin_in_db.description} != {plugin.description}"
        )
        to_update = True
        database_properties["Description"] = plugin.description
    if (plugin_in_db.fundingUrl != plugin.fundingUrl) and plugin.fundingUrl:
        console.log(
            f"[italic red]Mismatched fundingUrl: {plugin_in_db.fundingUrl} != {plugin.fundingUrl}"
        )
        to_update = True
        database_properties["Funding URL"] = plugin.fundingUrl

    if (plugin_in_db.isDesktopOnly != plugin.isDesktopOnly) and not error:
        console.log(
            f"[italic red]Mismatched isDesktopOnly: {plugin_in_db.isDesktopOnly} != {plugin.isDesktopOnly}"
        )
        # not that the value is invert; if the plugin is mobile friendly, the value is False
        to_update = True
        database_properties["Mobile friendly"] = not plugin.isDesktopOnly

    if plugin_in_db.last_commit_date != plugin.last_commit_date:
        console.log(
            f"[italic red]Mismatched last_commit_date: {plugin_in_db.last_commit_date} != {plugin.last_commit_date}"
        )
        last_commit_date = plugin.last_commit_date
        if isinstance(last_commit_date, datetime):
            last_commit_date = last_commit_date.isoformat()
        database_properties["Last Commit Date"] = last_commit_date
    if (plugin_in_db.etag != plugin.etag) and plugin.etag:
        console.log(
            f"[italic red]Mismatched etag: {plugin_in_db.etag} != {plugin.etag}"
        )
        to_update = True
        database_properties["ETAG"] = plugin.etag
    status = generate_activity_tag(plugin)
    if (plugin_in_db.status != status) and plugin_in_db.status not in [
        State.ARCHIVED,
        State.MAINTENANCE,
    ]:
        console.log(f"[italic red]Mismatched status: {plugin_in_db.status} != {status}")
        to_update = True
        database_properties["Status"] = status
    if (plugin_in_db.repo != plugin.repo) and plugin.repo:
        console.log(
            f"[italic red]Mismatched repo: {plugin_in_db.repo} != {plugin.repo}"
        )
        to_update = True
        database_properties["Github Link"] = f"https://github.com/{plugin.repo}"
    if to_update:
        console.log(f"Updating {plugin_in_db.name}")
        seatable.update_row("Plugins", db["_id"], database_properties)
    track_info.Progress.update(track_info.Task, advance=1)
