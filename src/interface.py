from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class EtagPlugins(BaseModel):
    etag: str
    plugin_id: str
    commit_date: str


class PluginItems(BaseModel):
    id: str
    name: str
    description: str
    repo: str
    author: str
    fundingUrl: Optional[str] = None  # noqa
    isDesktopOnly: Optional[bool] = None  # noqa
    last_commit_date: Optional[str | datetime] = None
    etag: Optional[str] = None
    status: Optional[str] = None


class Manifest(BaseModel):
    id: str
    name: str
    version: str
    minAppVersion: str  # noqa
    description: str
    author: str
    authorUrl: str  # noqa
    fundingUrl: Any  # noqa
    isDesktopOnly: Optional[bool] = None  # noqa


class RepositoryInformationDate(BaseModel):
    last_commit_date: Optional[str | datetime] = None
    etag: Optional[str] = None
