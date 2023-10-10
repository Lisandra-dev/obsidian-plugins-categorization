from pydantic import BaseModel


class EtagPlugins(BaseModel):
    etag: str
    plugins: str
    commit_date: str
