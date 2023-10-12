import json
import urllib.request
from datetime import datetime

from interface import PluginItems
from seatable_api.date_utils import dateutils


def generate_activity_tag(plugin: PluginItems) -> str:
    if plugin.last_commit_date:
        today = dateutils.now()
        last_commit_date = plugin.last_commit_date
        if isinstance(last_commit_date, datetime):
            last_commit_date = last_commit_date.isoformat()
        diff_time = dateutils.datediff(last_commit_date, today, unit="D")
        if diff_time and diff_time < 365:  # noqa
            return "ACTIVE"
        else:
            return "STALE"
    return "STALE"


def get_len_of_plugin() -> int:
    url = "https://raw.githubusercontent.com/obsidianmd/obsidian-releases/master/community-plugins.json"
    content = urllib.request.urlopen(url).read()
    data = json.loads(content)
    return len(data)
