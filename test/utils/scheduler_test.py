from unittest import mock

import psycopg2
import pytest
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from models.website import ErrorModel
from service.database.connector import DatabaseConnector
from service.utils import scheduler
from service.utils.scheduler import scheduled_jobs_map
from test.service.test_constants import TestConfig, TestConstants

test_scheduler = BackgroundScheduler()

db_connector = None


@pytest.fixture(autouse=True, scope='function')
def mock_db_operations():
    """
    Patching psycopg2.connect function to mock necessary methods used while calling the database.
    Refresh the job scheduler before every test.
    """
    with mock.patch('psycopg2.connect'):
        global db_connector
        db_connector = DatabaseConnector(database=TestConfig.DB_NAME,
                                         host=TestConfig.DB_HOST,
                                         port=TestConfig.DB_PORT,
                                         user=TestConfig.DB_USER,
                                         password=TestConfig.DB_PASSWORD)
        global test_scheduler
        test_scheduler = BackgroundScheduler()
        yield


def test_add_job_if_applicable():
    """
    Nominal Scenario: The job is added to the DB, then it is added to the scheduler.
    Expect a new job added to the scheduler, with correct trigger interval.
    """
    with mock.patch('service.utils.scheduler.get_website_by_url') as mock_db_response:
        mock_db_response.return_value = TestConstants.website_model
        scheduler.add_job_if_applicable(db_connector, TestConstants.website_model, test_scheduler, False)
        scheduled_job = test_scheduler.get_job(TestConstants.website_id)

    assert scheduled_job is not None
    assert scheduled_job.trigger.interval.seconds == TestConstants.website_monitoring_interval


def test_add_job_if_applicable_return_exception():
    """
    When adding a job, the DB connection raises an exception.
    Expect a response of type ErrorModel.
    """
    with mock.patch('service.utils.scheduler.get_website_by_url') as mock_db_response:
        mock_db_response.side_effect = psycopg2.Error("Error raised for tests")
        response_error = scheduler.add_job_if_applicable(db_connector, TestConstants.website_model, test_scheduler,
                                                         False)
    assert isinstance(response_error, ErrorModel)


def test_update_job_if_applicable_job_exist_in_scheduler():
    """
    Test updating a job that exist in the scheduler: Update the trigger interval.
    Add a job to the scheduler and to the scheduled_jobs_map to make sure the job exist.
    Expect the same job (same job_id) with different trigger interval
    The executed function will change, but it is not the goal of our test
    """
    test_scheduler.add_job(lambda: print("Test"), IntervalTrigger(seconds=10), id=TestConstants.website_id)
    scheduled_jobs_map[TestConstants.website_id] = TestConstants.website_model
    with mock.patch('service.utils.scheduler.get_website_by_url') as mock_db_response:
        mock_db_response.return_value = TestConstants.website_model
        scheduler.update_job_if_applicable(db_connector, TestConstants.website_model, test_scheduler)

        scheduled_job = test_scheduler.get_job(TestConstants.website_id)
        assert scheduled_job.trigger.interval.seconds == TestConstants.website_monitoring_interval


def test_update_job_if_applicable_job_does_not_exist_in_db():
    """
    Updating a job that does not exist in the DB result in an ErrorModel object returned.
    """
    with mock.patch('service.utils.scheduler.get_website_by_url') as mock_db_response:
        mock_db_response.return_value = None
        response_error = scheduler.update_job_if_applicable(db_connector, TestConstants.website_model, test_scheduler)

        assert isinstance(response_error, ErrorModel)


def test_update_job_if_applicable_job_when_db_returns_an_exception():
    """
    The job exist in the DB and in the scheduled_jobs_map, but when updating, a database connector exception is raised.
    Expect an ErrorModel object, and no change in the scheduled job.
    :return:
    """
    test_scheduler.add_job(lambda: print("Test"), IntervalTrigger(seconds=10), id=TestConstants.website_id)
    scheduled_jobs_map[TestConstants.website_id] = TestConstants.website_model

    with mock.patch('service.utils.scheduler.update_website') as mock_db_update, \
            mock.patch('service.utils.scheduler.get_website_by_url') as mock_db_response:
        mock_db_response.return_value = TestConstants.website_model
        mock_db_update.side_effect = psycopg2.Error("Error raised for tests")
        response_error = scheduler.update_job_if_applicable(db_connector, TestConstants.website_model, test_scheduler)
        scheduled_job = test_scheduler.get_job(TestConstants.website_id)

        assert isinstance(response_error, ErrorModel)
        assert scheduled_job.trigger.interval.seconds == 10
