from interface import PluginItems, State
from seatable_api import Base
from utils import convert_time, generate_activity_tag


def add_new(plugin: PluginItems, seatable: Base) -> None:
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
