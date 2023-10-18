from typing import Any

import pandas as pd
from interface import PluginItems
from seatable_api import Base
from utils import unique_category


def translate_keywords_from_plugin(plugin: PluginItems, keywords: pd.DataFrame) -> list:
    description = plugin.description
    name = plugin.name
    plugin_keywords = []
    for index, row in keywords.iterrows():
        if row.Keyword in description.lower() or row.Keyword.lower() in name.lower():
            plugin_keywords += row["Category Record"]
    # remove duplicate in plugin_keywords
    return unique_category(plugin_keywords)


def new_keywords_list(
    database_property: dict[str, Any], new_keywords: list[Any]
) -> list:
    if not database_property["Auto-Suggested Categories"]:
        return new_keywords
    else:
        row_ids = set(
            item["row_id"] for item in database_property["Auto-Suggested Categories"]
        )
        for keyword in new_keywords:
            if keyword["row_id"] not in row_ids:
                database_property["Auto-Suggested Categories"].append(keyword)
                row_ids.add(keyword["row_id"])
        return database_property["Auto-Suggested Categories"]


def add_new_keywords(
    database_property: dict[str, Any], plugin: PluginItems, keywords: pd.DataFrame
) -> list:
    new_category = translate_keywords_from_plugin(plugin, keywords)
    category_to_add = []
    if not database_property["Auto-Suggested Categories"]:
        return new_category
    else:  # append ?
        row_ids = set(
            item["row_id"] for item in database_property["Auto-Suggested Categories"]
        )
        for category in new_category:
            if category["row_id"] not in row_ids:
                category_to_add.append(category)
                row_ids.add(category["row_id"])
        return category_to_add


def get_linked_table(seatable: Base) -> str:
    return seatable.get_column_link_id("Plugins", "Auto-Suggested Categories")


def update_links(
    seatable: Base, linked_id: str, keywords: list[Any], row_id: str
) -> None:
    for category in keywords:
        seatable.add_link(
            linked_id,
            "Categories",
            "Plugins",
            category["row_id"],
            row_id,
        )
