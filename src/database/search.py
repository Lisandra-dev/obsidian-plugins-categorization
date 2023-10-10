import pandas as pd
from interface import EtagPlugins


def get_etags_by_plugins(db: pd.DataFrame) -> list[EtagPlugins]:
    all_plugins = db.to_dict("records")
    all_etags = []
    for plugin in all_plugins:
        etag = EtagPlugins(
            etag=plugin["ETAG"],
            plugin_id=plugin["ID"],
            commit_date=plugin["Last commit date"],
        )
        all_etags.append(etag)
    return all_etags
