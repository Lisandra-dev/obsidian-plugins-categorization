import datetime
import os
import sys

import pandas as pd
from database.add_new import add_new
from database.search import (
    get_etags_by_plugins,
    plugin_is_in_database,
    search_deleted_plugin,
)
from database.update import update_old_entry
from dotenv import load_dotenv
from get_plugins import get_raw_data
from github import Auth, Github
from interface import PluginItems
from rich import print
from rich.console import Console
from seatable_api import Base

load_dotenv()


def get_database() -> tuple[pd.DataFrame, Base]:
    server_url = "https://cloud.seatable.io"
    token = os.getenv("SEATABLE_API_TOKEN")
    table_name = "Plugins"
    base = Base(token, server_url)
    base.auth()
    ## Get rows from 'Plugins' table
    lst_seatable = base.query("SELECT * FROM `" + table_name + "` LIMIT 10000")

    df_seatable = pd.json_normalize(lst_seatable)
    return df_seatable, base


def main() -> None:
    auth = Auth.Token(os.getenv("GITHUB_TOKEN"))  # type: ignore
    octokit: Github = Github(auth=auth)
    start_time = datetime.datetime.now()
    # get rate limit
    max_length: int | None = None
    dev = len(sys.argv) > 1 and sys.argv[1] == "dev"
    if dev:
        max_length = 5
    rate_limit = octokit.get_rate_limit()
    print(f"Rate limit: {rate_limit.core.remaining}/{rate_limit.core.limit}")
    console = Console()
    with console.status("[bold green]Fetching data from SeaTable", spinner="dots"):
        db, base = get_database()
        commits_from_db = get_etags_by_plugins(db)
    console.log(f"Found {len(db)} plugins in the database")

    with console.status("[bold green]Fetching data from GitHub", spinner="dots"):
        all_plugins = get_raw_data(commits_from_db, max_length=max_length)  # noqa
    console.log(f"Found {len(all_plugins)} plugins on GitHub")
    if dev:
        test_plugin = {
            "id": "test",
            "name": "test",
            "description": "test",
            "repo": "test",
            "author": "test",
            "fundingUrl": "test",
            "isDesktopOnly": False,
            "last_commit_date": datetime.datetime.now(),
            "etag": "test",
            "status": "ACTIVE",
        }

        all_plugins.append(PluginItems(**test_plugin))

    with console.status("[bold green]Updating database", spinner="dots"):
        for plugin in all_plugins:
            if plugin_is_in_database(db, plugin):
                console.print(f"• Updating {plugin.name}")
                update_old_entry(plugin, db, base, console)
            else:
                console.print(f"• Adding {plugin.name}")
                add_new(plugin, base)

    with console.status("[bold red]Searching for deleted plugins", spinner="dots"):
        deleted_plugins = search_deleted_plugin(db, all_plugins, max_length=max_length)
        if deleted_plugins:
            console.log(f"Found {len(deleted_plugins)} deleted plugins")
            for plugin in deleted_plugins:
                if not dev:
                    base.delete_row("Plugins", plugin["_id"])

        else:
            console.log("No deleted plugins found")

    end_time = datetime.datetime.now()
    diff_time_in_min = (end_time - start_time).total_seconds() / 60
    console.log(f"Finished in {diff_time_in_min:.2f} minutes")


if __name__ == "__main__":
    main()
