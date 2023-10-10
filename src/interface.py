from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EtagPlugins(BaseModel):
    etag: Optional[str] = None
    plugin_id: str
    commit_date: Optional[str | datetime] = None


class PluginItems(BaseModel):
    id: str
    name: str
    description: str
    repo: str
    author: Optional[str] = None
    fundingUrl: Optional[str] = None  # noqa
    isDesktopOnly: Optional[bool] = None  # noqa
    last_commit_date: Optional[str | datetime] = None
    etag: Optional[str] = None
    status: Optional[str] = None


class Manifest(BaseModel):
    id: str
    name: str
    version: str
    minAppVersion: Optional[str] = None  # noqa
    description: str
    author: Optional[str] = None
    authorUrl: Optional[str] = None  # noqa
    fundingUrl: Optional[dict | str] = None  # noqa
    isDesktopOnly: Optional[bool] = None  # noqa


class RepositoryInformationDate(BaseModel):
    last_commit_date: Optional[str | datetime] = None
    etag: Optional[str] = None
