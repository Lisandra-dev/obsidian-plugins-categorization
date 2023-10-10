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
