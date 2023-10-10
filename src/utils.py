from datetime import datetime

from interface import PluginItems


def generate_activity_tag(plugin: PluginItems) -> str:
    if plugin.last_commit_date:
        today = datetime.today()
        if isinstance(plugin.last_commit_date, str):
            last_commit_date = datetime.strptime(plugin.last_commit_date, "%Y-%m-%d")
        else:
            last_commit_date = plugin.last_commit_date
        diff_time = today - last_commit_date
        diff_days = diff_time.days
        if diff_days < 365:  # noqa
            return "ACTIVE"
        else:
            return "STALE"
    return "STALE"
