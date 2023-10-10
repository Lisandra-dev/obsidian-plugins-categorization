import os

import pandas as pd
from database.search import get_etags_by_plugins
from dotenv import load_dotenv
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
    lst_seatable = base.query(
        "SELECT _id, ID, Name, Description, `Github Link` FROM `"
        + table_name
        + "` LIMIT 10000"
    )

    df_seatable = pd.json_normalize(lst_seatable)
    return df_seatable


def main() -> None:
    auth = Auth.Token(os.getenv("GITHUB_TOKEN"))
    print(auth)
    octokit = Github(auth=auth)
    pd.Timestamp.now()
    # get rate limit
    rate_limit = octokit.get_rate_limit()
    print(f"Rate limit: {rate_limit.core.remaining}/{rate_limit.core.limit}")
    snipper = Halo(text="Fetching data from SeaTable", spinner="dots")
    snipper.start()
    db = get_database()
    snipper.succeed("Data fetched from SeaTable")
    commits_from_db = get_etags_by_plugins(db)
    print(commits_from_db)


if __name__ == "__main__":
    main()
