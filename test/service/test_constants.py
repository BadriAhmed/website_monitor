from datetime import datetime

from models.website import Website, WebsitesList, MonitoringEntriesList


class TestConstants:
    website_id = "1"
    website_keyword = "test"
    website_url = "https://testwebsite.com"
    website_monitoring_interval = 60
    website_regex = "regex"

    db_website = (1, website_url, 60, "regex")
    db_website2 = (2, website_url, 120, "regex2")
    db_website_list = [db_website, db_website2]

    website_model = Website.parse_tuple(db_website)
    websites_list = WebsitesList.parse_from_list([db_website, db_website2])

    db_monitoring_entry1 = (1, 1, 200, datetime.now(), 9.99, "regex_response")
    db_monitoring_entry2 = (2, 1, 200, datetime.now(), 10.99, "regex_response")
    db_monitoring_entries = [db_monitoring_entry1, db_monitoring_entry2]
    monitoring_entries_list = MonitoringEntriesList.parse_from_list(db_monitoring_entries)


class TestConfig:
    DB_NAME = "test_db"
    DB_USER = "test_user"
    DB_PASSWORD = "test_password"
    DB_HOST = "127.0.0.1"
    DB_PORT: str = "8000"
