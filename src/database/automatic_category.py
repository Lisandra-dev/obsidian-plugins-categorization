from typing import Any

import pandas as pd
from interface import PluginItems
from seatable_api import Base
from utils import unique_category


def translate_keywords_from_plugin(plugin: PluginItems, keywords: pd.DataFrame) -> list:
    description = (
        plugin.description.lower().replace("obsidian", "").replace("-", " ").split(" ")
    )
    name = plugin.name.lower().replace("obsidian", "").replace("-", " ").split(" ")
    plugin_keywords = []
    for index, row in keywords.iterrows():
        if row.Keyword.lower() in description or row.Keyword.lower() in name:
            plugin_keywords += row["Category Record"]
    # remove duplicate in plugin_keywords
    return unique_category(plugin_keywords)


def get_linked_table(seatable: Base) -> str:
    return seatable.get_column_link_id("Plugins", "Auto-Suggested Categories")


def deleted_keywords(
    database_property: dict[str, Any],
    keywords: pd.DataFrame,
    plugin: PluginItems,
) -> list[Any]:
    default_keywords = translate_keywords_from_plugin(plugin, keywords)
    if database_property["Auto-Suggested Categories"] is None:
        return []
    row_ids = set(
        item["row_id"] for item in database_property["Auto-Suggested Categories"]
    )
    deleted = []
    for row_id in row_ids:
        if row_id not in [item.get("row_id", None) for item in default_keywords]:
            deleted.append(
                {
                    "row_id": row_id,
                    "name": [
                        name.get("display_value")
                        for name in database_property["Auto-Suggested Categories"]
                        if name.get("row_id") == row_id
                    ][0],
                }
            )
    return deleted


def update_links(
    seatable: Base,
    linked_id: str,
    keywords: list[Any],
    row_id: str,
    deleted_keywords: list[Any] | None = None,
) -> None:
    for category in keywords:
        seatable.add_link(
            linked_id,
            "Categories",
            "Plugins",
            category["row_id"],
            row_id,
        )
    if deleted_keywords:
        for keyword in deleted_keywords:
            seatable.remove_link(
                linked_id, "Categories", "Plugins", keyword["row_id"], row_id
            )


def remove_duplicate(keywords_in_db: list[Any]) -> list[Any]:
    row_ids = set(item["row_id"] for item in keywords_in_db)
    cleaned_keywords = []
    for row_id in row_ids:
        if row_id not in [item.get("row_id", None) for item in cleaned_keywords]:
            cleaned_keywords.append(
                [item for item in keywords_in_db if item.get("row_id") == row_id][0]
            )
    return cleaned_keywords
