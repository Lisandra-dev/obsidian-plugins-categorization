from typing import Any

import pandas as pd
from interface import EtagPlugins, PluginItems
from rich.console import Console
from seatable_api import Base


def get_etags_by_plugins(db: pd.DataFrame) -> list[EtagPlugins]:
    all_plugins = db.to_dict("records")
    all_etags = []
    for plugin in all_plugins:
        etag = EtagPlugins(
            etag=plugin["ETAG"],
            plugin_id=plugin["ID"],
            commit_date=plugin["Last Commit Date"],
        )
        all_etags.append(etag)
    return all_etags


def get_plugin_in_database(db: pd.DataFrame, plugin: PluginItems) -> pd.DataFrame:
    return db.loc[db["ID"] == plugin.id]


def plugin_is_in_database(db: pd.DataFrame, plugin: PluginItems) -> bool:
    return not db.loc[db["ID"] == plugin.id].empty


def search_deleted_plugin(
    seatable: pd.DataFrame, all_plugins: list[PluginItems]
) -> list[Any]:
    deleted_plugins = []
    for index, row in seatable.iterrows():
        plugin = [plugin for plugin in all_plugins if plugin.id == row["ID"]]
        if len(plugin) == 0:
            deleted_plugins.append(row)
    return deleted_plugins


def delete_duplicate(db: pd.DataFrame, seatable: Base, console: Console) -> None:
    duplicate = db[db.duplicated("ID", keep=False)]
    if duplicate.empty:
        console.log("[underline grey]No duplicate found")
        return
    duplicated_ids = list(set(duplicate["_id"].tolist()))
    seatable.batch_delete_rows("Plugins", duplicated_ids)
    console.log(f"[underline grey]Deleted {len(duplicated_ids)} duplicate(s)")
