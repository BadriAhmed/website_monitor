from datetime import datetime
from http import HTTPStatus
from typing import List, Optional

import validators
from pydantic import BaseModel, validator


class Website(BaseModel):
    website_id: Optional[int]
    website_url: str
    monitoring_interval: int
    regex: Optional[str]

    @validator('website_url')
    def must_be_a_valid_url(cls, website_url):
        if not validators.url(website_url):
            raise ValueError('must be a valid url format')
        return website_url

    @classmethod
    def parse_tuple(cls, obj: tuple):
        return Website(website_id=obj[0],
                       website_url=obj[1],
                       monitoring_interval=obj[2],
                       regex=obj[3])


class WebsitesList(BaseModel):
    websites_list = List[Website]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def parse_from_list(cls, lst: list):
        return [Website.parse_tuple(website) for website in lst]


class MonitoringEntry(BaseModel):
    id: Optional[int]
    website_id: int
    http_status: int
    entry_timestamp: datetime
    response_time: Optional[float]
    regex_response: Optional[str]

    @classmethod
    def parse_tuple(cls, obj: tuple):
        return MonitoringEntry(id=obj[0],
                               website_id=obj[1],
                               http_status=obj[2],
                               entry_timestamp=obj[3],
                               response_time=obj[4],
                               regex_response=obj[5])


class MonitoringEntriesList(BaseModel):
    monitoring_entries_list = List[MonitoringEntry]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def parse_from_list(cls, lst: list):
        return [MonitoringEntry.parse_tuple(entry) for entry in lst]


class ErrorModel(BaseModel):
    error: str
    description: str
    http_status: HTTPStatus
