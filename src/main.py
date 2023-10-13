import datetime
import os
import sys

import pandas as pd
from database.add_new import add_new
from database.search import (
    delete_duplicate,
    get_etags_by_plugins,
    plugin_is_in_database,
    search_deleted_plugin,
)
from database.update import update_old_entry
from dotenv import load_dotenv
from get_plugins import get_raw_data
from github import Auth, Github
from interface import EtagPlugins, PluginItems, Task_Info, UnInt
from rich import print
from rich.console import Console
from rich.progress import Progress
from seatable_api import Base
from typing_extensions import Literal
from utils import get_len_of_plugin

load_dotenv()


def get_database(
    env: Literal["dev", "prod", "test", None] = None
) -> tuple[pd.DataFrame, Base]:
    server_url = "https://cloud.seatable.io"
    token = os.getenv("SEATABLE_API_TOKEN_PROD")
    if env == "dev":
        token = os.getenv("SEATABLE_API_TOKEN_DEV")
    elif env == "test":
        token = os.getenv("SEATABLE_API_TOKEN_TESTS")

    if not token:
        raise ValueError("No token found")

    table_name = "Plugins"
    base = Base(token, server_url)
    base.auth()
    ## Get rows from 'Plugins' table
    lst_seatable = base.query("SELECT * FROM `" + table_name + "` LIMIT 10000")

    df_seatable = pd.json_normalize(lst_seatable)
    return df_seatable, base


def fetch_seatable_data(
    console: Console
) -> tuple[pd.DataFrame, Base, list[EtagPlugins]]:
    with console.status("[bold green]Fetching data from SeaTable", spinner="dots"):
        db, base = get_database(fetch_arguments())
        commits_from_db = get_etags_by_plugins(db)
    console.log(f"Found {len(db)} plugins in the database")
    return db, base, commits_from_db


def fetch_arguments() -> Literal["dev", "prod", "test", None]:
    env = "prod"
    if len(sys.argv) > 1:
        if sys.argv[1] == "dev":
            env = "dev"
        elif sys.argv[1] == "test":
            env = "test"
    return env


def fetch_github_data(
    console: Console,
    commits_from_db: list[EtagPlugins],
    max_length: UnInt = None,
) -> list[PluginItems]:
    len_plugins = get_len_of_plugin()
    if max_length:
        len_plugins = max_length
    console.log(f"Found {len_plugins} plugins on GitHub")
    all_plugins = []
    with Progress() as progress:
        plugin_progress = progress.add_task(
            "[bold green]Fetching data", total=len_plugins
        )

        task_info = Task_Info(progress, plugin_progress)
        while not task_info.Progress.finished:
            all_plugins, task_info = get_raw_data(
                commits_from_db, task_info, max_length=max_length
            )  # noqa
    console.log(f"Found {len(all_plugins)} plugins on GitHub")
    return all_plugins


def track_plugins_update(
    all_plugins: list[PluginItems], db: pd.DataFrame, base: Base
) -> None:
    with Progress() as progress:
        update = progress.add_task(
            "[bold green]Updating plugins", total=len(all_plugins)
        )
        task_info = Task_Info(progress, update)
        for plugin in all_plugins:
            if plugin_is_in_database(db, plugin):
                # console.print(f"• Updating {plugin.name}")
                task_info.Progress.update(
                    task_info.Task, description=f"[italic green]Updating {plugin.name}"
                )
                update_old_entry(plugin, db, base, task_info)
            else:
                task_info.Progress.update(
                    task_info.Task, description=f"[underline blue]Adding {plugin.name}"
                )
                add_new(plugin, base)
                task_info.Progress.update(task_info.Task, advance=1)


def track_plugin_deleted(  # noqa
    console: Console,
    all_plugins: list[PluginItems],
    db: pd.DataFrame,
    base: Base,
) -> None:
    with console.status("[bold red]Searching for deleted plugins", spinner="dots"):
        deleted_plugins = search_deleted_plugin(db, all_plugins)
    if deleted_plugins:
        console.log(f"Found {len(deleted_plugins)} deleted plugins")
        with Progress() as progress:
            delete = progress.add_task(
                "[bold red]Deleting plugins", total=len(deleted_plugins)
            )
            task_info = Task_Info(progress, delete)
            for plugin in deleted_plugins:
                base.delete_row("Plugins", plugin["_id"])
                task_info.Progress.update(
                    task_info.Task,
                    description=f"[italic red]Deleted {plugin['Name']}",
                    advance=1,
                )

    else:
        console.log("No deleted plugins found")


def main() -> None:
    auth = Auth.Token(os.getenv("GITHUB_TOKEN"))  # type: ignore
    octokit: Github = Github(auth=auth)
    start_time = datetime.datetime.now()
    # get rate limit
    max_length: int | None = None
    dev = fetch_arguments() == "test"
    if dev:
        max_length = 5
    rate_limit = octokit.get_rate_limit()
    print(f"Rate limit: {rate_limit.core.remaining}/{rate_limit.core.limit}")
    console = Console()

    db, base, commits_from_db = fetch_seatable_data(console)
    all_plugins = fetch_github_data(console, commits_from_db, max_length=max_length)

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

    track_plugins_update(all_plugins, db, base)
    if not dev:
        track_plugin_deleted(console, all_plugins, db, base)

    if not dev:
        delete_duplicate(db, base, console)
    else:  # find len of duplicate
        duplicate = db[db.duplicated("ID", keep=False)]
        duplicated_ids = list(set(duplicate["id"].tolist()))
        console.log(
            f"Found {len(duplicated_ids)} duplicated plugins:\n• {"\n• ".join(duplicated_ids)} "
        )

    end_time = datetime.datetime.now()
    diff_time_in_min = (end_time - start_time).total_seconds() / 60
    console.log(f"Finished in {diff_time_in_min:.2f} minutes")


if __name__ == "__main__":
    main()
