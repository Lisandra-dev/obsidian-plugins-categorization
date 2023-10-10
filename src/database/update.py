import pandas as pd
from interface import PluginItems
from pandas.core.series import Series
from rich.console import Console
from seatable_api import Base
from utils import generate_activity_tag

from database.search import get_plugin_in_database


def update_old_entry(
    plugin: PluginItems, database: pd.DataFrame, seatable: Base, console: Console
) -> None:
    db = get_plugin_in_database(database, plugin).iloc[0]
    plugin_in_db = PluginItems(
        id=str(db["ID"]),
        name=str(db["Name"]),
        description=str(db["Description"]),
        repo=str(db["Github Link"].replace("https://github.com/", "")),
        author=str(db["Author"]) if db["Author"] else None,
        fundingUrl=str(db["Funding URL"]) if db["Funding URL"] else None,
        isDesktopOnly=bool(db["Mobile friendly"]) if db["Mobile friendly"] else False,
        last_commit_date=(db["Last Commit Date"]).strftime("%Y-%m-%d")
        if db["Last Commit Date"]
        else None,
        etag=str(db["ETAG"]) if db["ETAG"] else None,
        status=str(db["Status"]) if db["Status"] else None,
    )

    error = db["Error"] if db["Error"] else None
    # check if the plugin has changed
    if (plugin_in_db.author != plugin.author) and plugin.author:
        console.log(f"Mismatched author: {plugin_in_db.author} != {plugin.author}")
        database_update(seatable, db, plugin.author, "Author")

    if (plugin_in_db.description != plugin.description) and plugin.description:
        console.log(
            f"Mismatched description: {plugin_in_db.description} != {plugin.description}"
        )
        database_update(seatable, db, plugin.description, "Description")
    if (plugin_in_db.fundingUrl != plugin.fundingUrl) and plugin.fundingUrl:
        console.log(
            f"Mismatched fundingUrl: {plugin_in_db.fundingUrl} != {plugin.fundingUrl}"
        )
        database_update(seatable, db, plugin.fundingUrl, "Funding URL")

    if (
        (plugin_in_db.isDesktopOnly != plugin.isDesktopOnly)
        and plugin.isDesktopOnly
        and not error
    ):
        console.log(
            f"Mismatched isDesktopOnly: {plugin_in_db.isDesktopOnly} != {plugin.isDesktopOnly}"
        )
        database_update(seatable, db, plugin.isDesktopOnly, "Mobile friendly")
    if (
        plugin_in_db.last_commit_date != plugin.last_commit_date
    ) and plugin.last_commit_date:
        console.log(
            f"Mismatched last_commit_date: {plugin_in_db.last_commit_date} != {plugin.last_commit_date}"
        )
        database_update(seatable, db, plugin.last_commit_date, "Last Commit Date")
    if (plugin_in_db.etag != plugin.etag) and plugin.etag:
        database_update(seatable, db, plugin.etag, "ETAG")
    status = generate_activity_tag(plugin)
    if (plugin_in_db.status != status) and (
        plugin_in_db.status != "MAINTENANCE" or plugin.status != "ARCHIVED"
    ):
        console.log(f"Mismatched status: {plugin_in_db.status} != {status}")
        database_update(seatable, db, status, "Status")


def database_update(
    seatable: Base,
    database: Series,
    value: any,  # type: ignore
    column: str,
) -> None:
    seatable.update_row("Plugins", database["_id"], {column: value})
