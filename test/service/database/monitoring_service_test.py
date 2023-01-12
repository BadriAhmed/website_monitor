from datetime import datetime
from unittest import mock

import pytest
from apscheduler.schedulers.background import BackgroundScheduler

from service.database import executions
from service.database.connector import DatabaseConnector
from test.service.test_constants import TestConstants, TestConfig

scheduler = BackgroundScheduler()

db_connector = None
mock_connect = None
mock_cursor = None


@pytest.fixture(autouse=True)
def mock_db_operations():
    """
    Patching psycopg2.connect function to mock necessary methods used while calling the database
    :return:
    """
    global mock_connect
    global mock_cursor
    with mock.patch('psycopg2.connect') as mock_connect:
        global db_connector
        db_connector = DatabaseConnector(database=TestConfig.DB_NAME,
                                         host=TestConfig.DB_HOST,
                                         port=TestConfig.DB_PORT,
                                         user=TestConfig.DB_USER,
                                         password=TestConfig.DB_PASSWORD)

        mock_cursor = mock_connect.return_value.cursor.return_value
        mock_cursor.fetchall.return_value = TestConstants.db_monitoring_entries
        yield


def test_get_monitoring_entries():
    result = executions.get_monitoring_entries(db_connector, website=TestConstants.website_url, offset=200, size=10)

    assert result == TestConstants.monitoring_entries_list
    mock_cursor.fetchall.assert_called()


def test_add_monitoring_entry():
    executions.add_monitoring_entry(db_connector, website_id=TestConstants.website_id, http_status=200,
                                    entry_timestamp=datetime.now(), response_time=9.99,
                                    regex_response=TestConstants.website_regex)
    mock_cursor.execute.assert_called()
    mock_connect().commit.assert_called()