from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import APIRouter, HTTPException

from configuration.config import DatabaseConfig
from models.website import Website, ErrorModel
from service.database.connector import DatabaseConnector
from service.database.executions import get_websites, search_website, get_monitoring_entries, init_database
from service.utils.scheduler import add_job_if_applicable, update_job_if_applicable
from service.utils.scheduler import schedule_jobs

website_monitor_router = APIRouter()

db_connector = DatabaseConnector(database=DatabaseConfig.DB_NAME,
                                 host=DatabaseConfig.DB_HOST,
                                 port=DatabaseConfig.DB_PORT,
                                 user=DatabaseConfig.DB_USER,
                                 password=DatabaseConfig.DB_PASSWORD)
init_database(db_connector)

scheduler = BackgroundScheduler()
scheduler.start()
schedule_jobs(db_connector, scheduler)


@website_monitor_router.get("/websites")
def get_jobs(page: int = 0, size: int = 10):
    offset = page * size
    return get_websites(db_connector, offset, size)


@website_monitor_router.get("/website")
def get_websites_by_keyword(keyword: str):
    return search_website(db_connector, keyword)


@website_monitor_router.post("/website", status_code=201)
def add_new_website(website: Website):
    response = add_job_if_applicable(db_connector, website, scheduler, )
    if type(response) is ErrorModel:
        raise HTTPException(status_code=response.http_status, detail=response.dict())


@website_monitor_router.put("/website", status_code=204)
def update_website(website: Website):
    response = update_job_if_applicable(db_connector, website, scheduler)
    if type(response) is ErrorModel:
        raise HTTPException(status_code=response.http_status, detail=response.dict())


@website_monitor_router.get("/monitoring")
def get_website_monitoring_data(website: str, page: int = 0, size: int = 10):
    offset = page * size
    return get_monitoring_entries(db_connector, website, offset, size)
