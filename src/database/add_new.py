import pandas as pd
from interface import PluginItems, State
from seatable_api import Base
from utils import convert_time, generate_activity_tag

from database import automatic_category


def add_new(
    plugin: PluginItems, seatable: Base, keywords: pd.DataFrame, linked_id: str
) -> None:
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

    rep = seatable.append_row("Plugins", new_database_entry)
    if not rep:
        return
    automatic = automatic_category.add_new_keywords(
        new_database_entry, plugin, keywords
    )
    automatic_category.update_links(seatable, linked_id, automatic, rep["_id"])
