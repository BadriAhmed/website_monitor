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
        mock_cursor.fetchone.return_value = TestConstants.db_website
        mock_cursor.fetchall.return_value = TestConstants.db_website_list
        yield


def test_get_all_websites():
    result = executions.get_all_websites(db_connector)

    assert result == TestConstants.websites_list
    mock_cursor.fetchall.assert_called()


def test_get_website_by_url():
    result = executions.get_website_by_url(db_connector, website_url=TestConstants.website_url)

    assert result == TestConstants.website_model
    mock_cursor.fetchone.assert_called()


def test_get_websites():
    result = executions.get_websites(db_connector, offset=1, size=10)

    assert result == TestConstants.websites_list
    mock_cursor.fetchall.assert_called()


def test_search_website():
    result = executions.search_website(db_connector, keyword=TestConstants.website_keyword)

    assert result == TestConstants.websites_list
    mock_cursor.fetchall.assert_called()


def test_add_website_with_regex():
    executions.add_website(db_connector, TestConstants.website_url, TestConstants.website_monitoring_interval,
                           TestConstants.website_regex)

    mock_cursor.execute.assert_called()
    mock_connect().commit.assert_called()


def test_add_website_without_regex():
    executions.add_website(db_connector, TestConstants.website_url, TestConstants.website_monitoring_interval, None)

    mock_cursor.execute.assert_called()
    mock_connect().commit.assert_called()


def test_update_website():
    executions.update_website(db_connector, TestConstants.website_url, TestConstants.website_monitoring_interval,
                              TestConstants.website_regex)

    mock_cursor.execute.assert_called()
    mock_connect().commit.assert_called()
