from http import HTTPStatus

import psycopg2
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger

from models.website import Website, ErrorModel
from service.database.connector import DatabaseConnector
from service.database.executions import get_all_websites, add_monitoring_entry, update_website, add_website, \
    get_website_by_url
from service.utils.helper import get_website_data, create_error_model

scheduled_jobs_map = {}


def schedule_jobs(db_connector: DatabaseConnector, job_scheduler):
    """
    Schedule a job to be executed periodically
    """
    try:
        websites = get_all_websites(db_connector)
    except psycopg2.Error as error:
        return create_error_model(db_connector, error)

    for job in websites:
        add_job_if_applicable(db_connector, job, job_scheduler, True)

    logger.info("Refreshing scheduled jobs")


def add_job_if_applicable(db_connector: DatabaseConnector, job: Website, job_scheduler, startup: bool = False):
    """
    Add a new  job to the scheduler if possible
    Add the job to the database if it is not the startup sequence
    """
    if not startup:
        try:
            add_website(db_connector, job.website_url, job.monitoring_interval, job.regex)
            job = get_website_by_url(db_connector, job.website_url)
        except psycopg2.Error as error:
            return create_error_model(db_connector, error)

    job_id = str(job.website_id)
    if job_id not in scheduled_jobs_map:
        scheduled_jobs_map[job_id] = job
        job_scheduler.add_job(lambda: execute_job(db_connector, job),
                              IntervalTrigger(seconds=job.monitoring_interval), id=job_id)

        logger.info("added job with id: {}".format(job_id))


def update_job_if_applicable(db_connector: DatabaseConnector, job: Website, job_scheduler):
    """
    Update job monitoring interval and/or regex expression if the job exist
    """
    old_job = get_website_by_url(db_connector, job.website_url)
    if old_job is None:
        return ErrorModel(error="No Job to Update",
                          description="The requested website url to monitor does not exist",
                          http_status=HTTPStatus.NOT_FOUND)

    job.website_id = str(old_job.website_id)

    if job.website_id not in scheduled_jobs_map:
        return

    new_interval = job.monitoring_interval
    new_regex = job.regex

    try:
        update_website(db_connector, job.website_url, new_interval, new_regex)
    except psycopg2.Error as error:
        return create_error_model(db_connector, error)

    job_scheduler.remove_job(job.website_id)
    job_scheduler.add_job(lambda: execute_job(db_connector, job),
                          IntervalTrigger(seconds=job.monitoring_interval), id=job.website_id)

    logger.info("Updated job with id: {}".format(job.website_id))


def execute_job(db_connector: DatabaseConnector, job: Website):
    """
    Execute a specific job at a specific timeframe
    Add a job monitoring entry in the database
    """
    response = get_website_data(job.website_url, job.website_id, job.regex)
    add_monitoring_entry(db_connector, job.website_id, response.http_status, response.entry_timestamp,
                         response.response_time, response.regex_response)
    logger.debug("Executing job {}".format(job.website_id))
