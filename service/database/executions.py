from datetime import datetime

from loguru import logger

from models.website import Website, WebsitesList, MonitoringEntriesList
from service.database.connector import DatabaseConnector
from service.database.queries import DatabaseQueries


def init_database(connector: DatabaseConnector):
    """
    Execute database initialization: Table creation
    """
    connector.execute_query(DatabaseQueries.create_tables)
    connector.commit_changes()
    logger.info('Database initialization successfully')


def get_all_websites(connector: DatabaseConnector) -> WebsitesList:
    """
    Get all websites to monitor from the DB
    """
    connector.execute_query(DatabaseQueries.get_all_websites)
    result = connector.fetch_all()
    return WebsitesList.parse_from_list(result)


def get_website_by_url(connector: DatabaseConnector, website_url: str):
    """
    Get a website using its url from the DB
    """
    connector.execute_query(DatabaseQueries.get_website_by_url.format(website_url))
    result = connector.fetch_one()
    if result is None:
        return
    return Website.parse_tuple(result)


def get_websites(connector: DatabaseConnector, offset: int, size: int) -> WebsitesList:
    """
    Get all websites to monitor from the DB with pagination
    """
    connector.execute_query(DatabaseQueries.get_websites.format(offset, size))
    result = connector.fetch_all()
    return WebsitesList.parse_from_list(result)


def search_website(connector: DatabaseConnector, keyword: str) -> Website:
    """
    Get websites using keyword search from the DB
    """
    connector.execute_query(DatabaseQueries.search_websites.format(keyword))
    result = connector.fetch_all()
    return WebsitesList.parse_from_list(result)


def add_website(connector: DatabaseConnector, website_url: str, monitoring_interval: int, regex_expression: str):
    """
    Add new website to the DB
    """
    if regex_expression is None:
        query = DatabaseQueries.add_website_without_regex.format(website_url, monitoring_interval)
    else:
        query = DatabaseQueries.add_website.format(website_url, monitoring_interval, regex_expression)
    connector.execute_query(query)
    connector.commit_changes()
    logger.debug("New website monitoring job added successfully  {}".format(website_url))


def update_website(connector: DatabaseConnector, website_url: str, monitoring_interval: int, regex_expression: str):
    """
    Update an existing website monitoring interval and/or regex expression
    """
    query = DatabaseQueries.update_website.format(monitoring_interval, regex_expression, website_url)
    connector.execute_query(query)
    connector.commit_changes()
    logger.debug("Website monitoring job updated {}".format(website_url))


def get_monitoring_entries(connector: DatabaseConnector, website: str, offset: int, size: int):
    """
        Get monitoring entry for a specific website using its URL
    """
    connector.execute_query(DatabaseQueries.get_website_monitoring_data.format(website, offset, size))
    result = connector.fetch_all()
    return MonitoringEntriesList.parse_from_list(result)


def add_monitoring_entry(connector: DatabaseConnector, website_id: int, http_status: int, entry_timestamp: datetime,
                         response_time: float, regex_response: list):
    """
        Add monitoring entry
    """
    if regex_response is None:
        query = DatabaseQueries.add_monitoring_entry_without_regex.format(website_id, http_status,
                                                                          entry_timestamp, response_time)
    else:
        regex_response = str(regex_response).replace("'", "")
        query = DatabaseQueries.add_monitoring_entry.format(website_id, http_status, entry_timestamp,
                                                            response_time, regex_response)
    connector.execute_query(query)
    connector.commit_changes()
    logger.debug("Monitoring entry added for  job {}".format(website_id))
