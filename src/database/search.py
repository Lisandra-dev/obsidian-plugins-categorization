import pandas as pd
from interface import EtagPlugins


def get_etags_by_plugins(db: pd.DataFrame) -> list[EtagPlugins]:
    all_plugins = db.to_dict("records")
    all_etags = []
    for plugin in all_plugins:
        etag = EtagPlugins(
            etag=plugin["etag"],
            plugins=plugin["plugins"],
            commit_date=plugin["commit_date"],
        )
        all_etags.append(etag)
    return all_etags
