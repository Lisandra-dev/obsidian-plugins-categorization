from datetime import datetime

from interface import PluginItems
from seatable_api import Base


def add_new(plugin: PluginItems, seatable: Base) -> None:
    mobile = not plugin.isDesktopOnly
    last_commit_date = plugin.last_commit_date
    if isinstance(last_commit_date, datetime):
        last_commit_date = last_commit_date.isoformat()

    new_database_entry = {
        "ID": plugin.id,
        "Name": plugin.name,
        "Description": plugin.description,
        "Github Link": f"https://github.com/{plugin.repo}",
        "Author": plugin.author,
        "Funding URL": plugin.fundingUrl,
        "Mobile friendly": mobile,
        "Last Commit Date": last_commit_date,  # convert to string
        "ETAG": plugin.etag,
        "Status": plugin.status,
        "Error": False,
        "Plugin Available": True,
    }
    seatable.append_row("Plugins", new_database_entry)
