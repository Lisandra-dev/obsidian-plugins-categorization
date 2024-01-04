from datetime import datetime
from enum import StrEnum
from typing import Any, NamedTuple, Optional

import pandas as pd
from pydantic import BaseModel, ConfigDict
from rich.console import Console
from rich.progress import Progress, TaskID
from seatable_api import Base

type UnString = Optional[str]
type UnDate = Optional[str | datetime]
type UnBool = Optional[bool]
type UnDict = Optional[dict | str]
type UnInt = Optional[int]


class State(StrEnum):
    ARCHIVED = "ARCHIVED"
    STALE = "STALE"
    ACTIVE = "ACTIVE"
    MAINTENANCE = "MAINTENANCE"


type UnState = Optional[State]


class EtagPlugins(BaseModel):
    etag: UnString = None
    plugin_id: str
    commit_date: UnDate = None


Task_Info = NamedTuple("task_info", [("Progress", Progress), ("Task", TaskID)])


class PluginItems(
    BaseModel,
):
    id: str
    name: str
    description: str
    repo: UnString = None
    author: UnString = None
    fundingUrl: UnString = None  # noqa
    isDesktopOnly: UnBool = None  # noqa
    last_commit_date: UnDate = None
    etag: UnString = None
    status: Optional[State] = None


class PluginProperties(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    database_properties: dict[str, Any]
    plugin: PluginItems
    seatable: PluginItems
    console: Console


class Manifest(BaseModel):
    id: str
    name: str
    version: str
    minAppVersion: UnString = None  # noqa
    description: str
    author: UnString = None
    authorUrl: UnString = None  # noqa
    fundingUrl: UnDict = None  # noqa
    isDesktopOnly: UnBool = None  # noqa


class RepositoryInformationDate(BaseModel):
    last_commit_date: UnDate = None
    etag: UnString = None


test_plugin: PluginItems = PluginItems(
    id="mara-test-database",
    name="mara DATABASE TEST",
    description="kindle keyboard",
    repo="test",
    author="test",
    fundingUrl="test",
    isDesktopOnly=False,
    last_commit_date="2023-09-01",
    etag="test",
    status=State.ACTIVE,
)


class DatabaseProperties(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    db: pd.DataFrame
    base: Base
    keywords: pd.DataFrame
    commit_date: list[EtagPlugins]
