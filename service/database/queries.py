class DatabaseQueries:
    create_tables = (
        "        CREATE TABLE IF NOT EXISTS websites("
        "        website_id serial PRIMARY KEY,"
        "        website_url VARCHAR NOT NULL UNIQUE,"
        "        monitoring_interval INTEGER NOT NULL UNIQUE,"
        "        regex VARCHAR,"
        "        CONSTRAINT"
        "        time_interval CHECK "
        "        (monitoring_interval::numeric >= 5::numeric AND monitoring_interval::numeric <= 300::numeric)"
        "    );"
        "    CREATE TABLE IF NOT EXISTS monitoring_data("
        "        id serial PRIMARY KEY,"
        "        website_id int NOT NULL,"
        "        http_status INTEGER NOT NULL,"
        "        entry_timestamp TIMESTAMP NOT NULL,"
        "        response_time FLOAT,"
        "        regex_response TEXT,"
        "        CONSTRAINT websites_foreign_key FOREIGN KEY (website_id)"
        "            REFERENCES websites(website_id)"
        "    );")

    add_website = (
        "INSERT INTO websites("
        "website_url, monitoring_interval, regex)"
        "VALUES ('{}',{}, '{}');")

    add_website_without_regex = (
        "INSERT INTO websites("
        "website_url, monitoring_interval)"
        "VALUES ('{}',{});")

    update_website = "UPDATE websites SET monitoring_interval={},regex='{}' WHERE website_url = '{}';"

    get_all_websites = "SELECT * FROM websites"

    get_websites = "SELECT * FROM websites OFFSET {} ROWS FETCH NEXT {} ROWS ONLY"

    search_websites = "SELECT * FROM websites WHERE website_url LIKE '%{}%';"

    add_monitoring_entry = (
        "INSERT INTO monitoring_data("
        "	website_id, http_status, entry_timestamp, response_time, regex_response)"
        "	VALUES ({}, {}, '{}', {}, '{}');")

    add_monitoring_entry_without_regex = (
        "INSERT INTO monitoring_data("
        "	website_id, http_status, entry_timestamp, response_time)"
        "	VALUES ({}, {}, '{}', {});")

    get_website_by_url = "SELECT * FROM websites WHERE website_url LIKE '{}'"

    get_website_monitoring_data = (
        "SELECT * "
        "FROM monitoring_data "
        "WHERE website_id = (SELECT website_id FROM websites WHERE website_url LIKE '{}') "
        "OFFSET {} ROWS FETCH NEXT {} ROWS ONLY")
