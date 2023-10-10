import datetime
import os
import sys

import pandas as pd
from database.search import get_etags_by_plugins
from database.update import update_old_entry
from dotenv import load_dotenv
from get_plugins import get_raw_data
from github import Auth, Github
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
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        max_length = 5
    rate_limit = octokit.get_rate_limit()
    print(f"Rate limit: {rate_limit.core.remaining}/{rate_limit.core.limit}")
    console = Console()
    with console.status("[bold green]Fetching data from SeaTable", spinner="dots"):
        db, base = get_database()
        commits_from_db = get_etags_by_plugins(db)
    console.log(f"Found {len(db)} plugins in the database")

    with console.status("[bold green]Fetching data from GitHub", spinner="dots"):
        all_plugins = get_raw_data(octokit, commits_from_db, max_length=max_length)  # noqa

    console.log(f"Found {len(all_plugins)} plugins on GitHub")

    with console.status("[bold green]Updating database", spinner="dots"):
        for plugin in all_plugins:
            console.print(f"• Updating {plugin.name}")
            update_old_entry(plugin, db, base, console)

    end_time = datetime.datetime.now()
    diff_time_in_min = (end_time - start_time).total_seconds() / 60
    console.log(f"Finished in {diff_time_in_min:.2f} minutes")


if __name__ == "__main__":
    main()
