import os
import sys

import pandas as pd
from database.search import get_etags_by_plugins
from dotenv import load_dotenv
from get_plugins import get_raw_data
from github import Auth, Github
from halo import Halo
from seatable_api import Base

load_dotenv()


def get_database() -> pd.DataFrame:
    server_url = "https://cloud.seatable.io"
    token = os.getenv("SEATABLE_API_TOKEN")
    table_name = "Plugins"
    base = Base(token, server_url)
    base.auth()
    ## Get rows from 'Plugins' table
    lst_seatable = base.query("SELECT * FROM `" + table_name + "` LIMIT 10000")

    df_seatable = pd.json_normalize(lst_seatable)
    return df_seatable


def main() -> None:
    auth = Auth.Token(os.getenv("GITHUB_TOKEN"))  # type: ignore
    print(auth)
    octokit: Github = Github(auth=auth)
    start_time = pd.Timestamp.now()
    # get rate limit
    max_length: int | None = None
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        max_length = 5
    rate_limit = octokit.get_rate_limit()
    print(f"Rate limit: {rate_limit.core.remaining}/{rate_limit.core.limit}")
    snipper = Halo(text="Fetching data from SeaTable", spinner="dots")
    snipper.start()
    db = get_database()
    snipper.succeed("Data fetched from SeaTable")
    commits_from_db = get_etags_by_plugins(db)
    spinner = Halo(text="Fetching data from GitHub", spinner="dots")
    spinner.start()
    all_plugins = get_raw_data(octokit, commits_from_db, max_length=max_length)
    spinner.succeed("Data fetched from GitHub")
    print(all_plugins)
    end_time = pd.Timestamp.now()
    print(f"Time elapsed: {end_time - start_time}")


if __name__ == "__main__":
    main()
