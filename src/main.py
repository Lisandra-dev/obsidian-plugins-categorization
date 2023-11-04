import argparse
import datetime
import os

import pandas as pd
from database.add_new import add_new
from database.automatic_category import get_linked_table
from database.search import (
    delete_duplicate,
    get_etags_by_plugins,
    plugin_is_in_database,
    search_deleted_plugin,
)
from database.update import update
from dotenv import load_dotenv
from get_plugins import read_plugin_json
from github import Auth, Github
from interface import (
    DatabaseProperties,
    EtagPlugins,
    PluginItems,
    Task_Info,
    UnInt,
    test_plugin,
)
from rich import print
from rich.console import Console
from rich.progress import Progress
from rich_argparse import RichHelpFormatter
from seatable_api import Base
from utils import get_len_of_plugin

load_dotenv()


def get_database(
    dev: bool = False,
) -> tuple[pd.DataFrame, Base]:
    server_url = "https://cloud.seatable.io"
    token = os.getenv("SEATABLE_API_TOKEN_PROD")
    if dev:
        token = os.getenv("SEATABLE_API_TOKEN_DEV")

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
    console: Console, dev: bool
) -> tuple[pd.DataFrame, Base, list[EtagPlugins]]:
    with console.status("[bold green]Fetching data from SeaTable", spinner="dots"):
        db, base = get_database(dev)
        commits_from_db = get_etags_by_plugins(db)
    console.log(f"Found {len(db)} plugins in the database")
    return db, base, commits_from_db


def get_keyword_to_category(seatable: Base) -> tuple[pd.DataFrame, str]:
    table_name = "Keywords to Category"
    keywords = seatable.query("SELECT * FROM `" + table_name + "` LIMIT 10000")
    df_seatable = pd.json_normalize(keywords)
    link_id = get_linked_table(seatable)
    return df_seatable, link_id


def fetch_github_data(
    console: Console,
    database: DatabaseProperties,
    max_length: UnInt = None,
    force: bool = False,
) -> list[PluginItems]:
    len_plugins = get_len_of_plugin()
    if max_length:
        len_plugins = max_length
    console.log(f"Found {len_plugins} plugins on GitHub")
    all_plugins = []
    commit_from_db = database.commit_date
    with Progress() as progress:
        plugin_progress = progress.add_task(
            "[bold green]Fetching data", total=len_plugins
        )

        task_info = Task_Info(progress, plugin_progress)
        while not task_info.Progress.finished:
            all_plugins, task_info = read_plugin_json(
                commit_from_db,
                task_info,
                max_length=max_length,
                force=force,
            )  # noqa
    console.log(f"Fetched {len(all_plugins)} plugins")
    return all_plugins


def track_plugins_update(
    all_plugins: list[PluginItems],
    databaseProperties: DatabaseProperties,  # noqa: N803
    link_id: str,
    archive: bool = False,
    new_only: bool = False,
) -> None:
    db = databaseProperties.db
    base = databaseProperties.base
    keywords = databaseProperties.keywords
    with Progress() as progress:
        update_task = progress.add_task(
            "[bold green]Updating plugins", total=len(all_plugins)
        )
        task_info = Task_Info(progress, update_task)
        for plugin in all_plugins:
            if plugin_is_in_database(db, plugin):
                task_info.Progress.update(
                    task_info.Task,
                    description=f"[italic green]Checking [{plugin.name}]",
                )
                if new_only:
                    continue  # skip to next plugin if new_only is True
                try:
                    update(
                        plugin, db, base, task_info, keywords, link_id, archive=archive
                    )
                except Exception as e:
                    console = task_info.Progress.console
                    console.log(
                        f"[bold red]Error with {plugin.name}[/bold red]: [underline]{e}"
                    )
                    task_info.Progress.update(task_info.Task, advance=1)
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


def main(dev: bool, archive: bool, new: bool, force: bool) -> None:
    auth = Auth.Token(os.getenv("GITHUB_TOKEN"))  # type: ignore
    octokit: Github = Github(auth=auth)
    start_time = datetime.datetime.now()
    # get rate limit
    max_length: int | None = None
    if dev:
        max_length = 5
    rate_limit = octokit.get_rate_limit()
    print(
        f"[underline italic]Starting with:[/underline italic]:\n• Dev: {dev}\n• Archive: {archive}\n• New: {new}\n• Force: {force}\n [italic]{start_time.strftime('%d/%m/%Y - %H:%M:%S')}[/italic]"
    )

    print(f"Rate limit: {rate_limit.core.remaining}/{rate_limit.core.limit}")
    console = Console()

    db, base, commits_from_db = fetch_seatable_data(console, dev)
    keywords, link_id = get_keyword_to_category(base)
    database_properties = DatabaseProperties(
        db=db, base=base, keywords=keywords, commit_date=commits_from_db
    )

    all_plugins = fetch_github_data(
        console, database_properties, max_length=max_length, force=force
    )

    if dev:
        all_plugins.append(test_plugin)
    track_plugins_update(all_plugins, database_properties, link_id, archive, new)
    if not dev:
        track_plugin_deleted(console, all_plugins, db, base)

    if not dev:
        delete_duplicate(db, base, console)
    else:  # find len of duplicate
        duplicate = db[db.duplicated("ID", keep=False)]
        if len(duplicate) > 0:
            duplicated_ids = list(set(duplicate["ID"].tolist()))
            console.log(
                f"Found {len(duplicated_ids)} duplicated plugins:\n• {"\n• ".join(duplicated_ids)} "
            )
        else:
            console.log("No duplicated plugins found")

    end_time = datetime.datetime.now()
    diff_time_in_min = (end_time - start_time).total_seconds() / 60
    console.log(f"Finished in {diff_time_in_min:.2f} minutes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update the plugins database",
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument(
        "-d",
        "--dev",
        action="store_true",
        help="Run the script in dev mode (use the Dev API token)",
    )
    parser.add_argument(
        "-a",
        "--archive",
        action="store_true",
        help="Search archived plugins, not in the main because of the rate limit",
    )
    parser.add_argument("-n", "--new", action="store_true", help="Add new plugins only")
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force update, create a new plugins.json file",
    )
    args = parser.parse_args()

    main(args.dev, args.archive, args.new, args.force)
