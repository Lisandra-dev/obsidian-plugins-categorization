import json
import urllib.request
from datetime import datetime
from typing import Any

from interface import PluginItems, State, UnDate
from seatable_api.date_utils import dateutils


def generate_activity_tag(plugin: PluginItems) -> State:
    if plugin.last_commit_date:
        today = dateutils.now()
        last_commit_date = plugin.last_commit_date
        if isinstance(last_commit_date, datetime):
            last_commit_date = last_commit_date.strftime("%Y-%m-%d")
        diff_time = dateutils.datediff(last_commit_date, today, unit="D")

        if diff_time and diff_time < 365 or diff_time == 0:  # noqa
            return State.ACTIVE
    return State.STALE


def get_len_of_plugin() -> int:
    url = "https://raw.githubusercontent.com/obsidianmd/obsidian-releases/master/community-plugins.json"
    content = urllib.request.urlopen(url).read()
    data = json.loads(content)
    return len(data)


def unique_category(new_category: list[Any]) -> list[Any]:
    unique_data = []
    seen_row_id = set()
    for item in new_category:
        if item["row_id"] not in seen_row_id:
            unique_data.append(item)
            seen_row_id.add(item["row_id"])
    return unique_data


def convert_time(date: UnDate) -> str | None:
    if not date:
        return None
    if isinstance(date, datetime):
        return date.strftime("%Y-%m-%d")
    else:
        try:
            return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
        except ValueError:
            return datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
