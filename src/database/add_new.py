from typing import Any

import pandas as pd
from interface import PluginItems, State
from seatable_api import Base
from utils import convert_time, generate_activity_tag

from database import automatic_category
from database.search import get_plugin_in_database


def auto_suggest_tags(  # noqa
    plugin: PluginItems,
    database_entry: dict[str, Any],
    keywords: pd.DataFrame,
    db: pd.DataFrame,
    seatable: Base,
    linked_id: str,
) -> None:
    automatic = automatic_category.add_new_keywords(database_entry, plugin, keywords)
    row_id = get_plugin_in_database(db, plugin).iloc[0]
    automatic_category.update_links(seatable, linked_id, automatic, row_id["_id"])


def add_new(plugin: PluginItems, seatable: Base) -> dict[str, Any]:
    new_database_entry = {
        "ID": plugin.id,
        "Name": plugin.name,
        "Description": plugin.description,
        "Github Link": f"https://github.com/{plugin.repo}",
        "Author": plugin.author,
        "Funding URL": plugin.fundingUrl,
        "Mobile friendly": not plugin.isDesktopOnly,
        "Last Commit Date": convert_time(plugin.last_commit_date),
        "ETAG": plugin.etag,
        "Status": State(generate_activity_tag(plugin)),
        "Error": False,
        "Plugin Available": True,
    }

    seatable.append_row("Plugins", new_database_entry)
    return new_database_entry
