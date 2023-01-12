import re
from datetime import datetime
from http import HTTPStatus

import psycopg2
import requests

from models.website import MonitoringEntry, ErrorModel
from service.database.connector import DatabaseConnector


def remove_html_tags(text):
    """Remove html tags from a string"""
    pattern = re.compile(r'<[^>]+>')
    return pattern.sub('', text)


def regex_matcher(regex_expression: str, text_input: str):
    """
    Find all expressions that matches the provided regex
    :param regex_expression
    :param text_input
    :return:
    """
    text_input = remove_html_tags(text_input)
    return re.findall(regex_expression, text_input)


def get_website_data(website_url: str, job_id: int, regex_expression: str):
    """
    Send a http request to a website, and get all necessary monitoring items to be stored
    :param website_url:
    :param job_id:
    :param regex_expression:
    :return:
    """
    try:
        with requests.get(website_url) as response:
            html = response.text
            response_time = response.elapsed.total_seconds()

            monitoring_entry = MonitoringEntry(website_id=job_id,
                                               http_status=response.status_code,
                                               entry_timestamp=datetime.now(),
                                               response_time=response_time)
            if regex_expression is not None:
                monitoring_entry.regex_response = regex_matcher(regex_expression, html)
            return monitoring_entry

    except requests.exceptions.ConnectionError:
        return MonitoringEntry(website_id=job_id,
                               http_status=999,
                               entry_timestamp=datetime.now(),
                               response_time=9999)


def create_error_model(db_connector: DatabaseConnector, exception: psycopg2.Error) -> ErrorModel:
    """
    Parse psycopg2 exception into error model
    :param exception:
    :return: ErrorModel
    """
    db_connector.rollback()
    return ErrorModel(error=exception.cursor.__str__(),
                      description=exception.pgerror.__str__(),
                      http_status=HTTPStatus.INTERNAL_SERVER_ERROR)
