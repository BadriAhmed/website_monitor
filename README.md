# Website Monitor

This repository is a project for a microservice that monitor webistes periodically.
This is basically a dummy project.
Feel free to try new things and experiment with it.
## Project structure

```
src
├── configuration          
|   └── config.py              # Configuration for database and server
├── models       
|   ├── website.py             # Models using pydantic
├── routers   
|   └── website                # Definition of endpoints
├── services          
|   ├── database        
|   |   ├── queries.py         # Queries written in SQL
|   |   ├── connector.py       # Database connector that uses psycopg2 to execute its tasks
|   |   └── executions.py      # Execute queries, and wrap results in pydantic models
|   └── utils        
|       ├── helper.py          # Helper functions
|       └── scheduler.py       # Include function related to the job scheduler,
|                                to create, update and execute jobs
└── test
    └── ...                    # Include all tests for the app. 
                                Structured the same way as the main package

```

## Requirements

The project uses python version 3.8 and above. The following Python modules are required:

* [psycopg2](http://initd.org/psycopg/) PostgreSQL database adapter used for the transactions
* [requests](http://www.python-requests.org/en/latest/) to send requests to the monitored websites
* [APScheduler](https://apscheduler.readthedocs.io/en/3.x/) Used to schedule monitoring tasks
* [FastApi](https://fastapi.tiangolo.com/) Webframework fpr creating endpoints
* [uvicorn](https://www.uvicorn.org/) ASGI web server
* [loguru](https://github.com/Delgan/loguru) Logging tool

## Database structure

#### Website Table:

Where the websites to monitor are stored

|        |       Column        |  Type   |         Constraint         |
|:------:|:-------------------:|:-------:|:--------------------------:|
| **PK** |     website_id      | INTEGER |          Not Null          |
|        |     website_url     | VARCHAR |          Not Null          |
|        | monitoring_interval | INTEGER | Not Null, in range (5,300) |
|        |        regex        | VARCHAR |                            |

This table store the **website_url** to be used to send Http requests within a **monitoring_interval** for monitoring
information to be extracted.
If a **regex** expression exists, it will be used to extract information for the response.

#### Monitoring_data Table:

Where the monitoring data for the websites to monitor are stored

|        |     Column      |   Type    |          Constraint           |
|:------:|:---------------:|:---------:|:-----------------------------:|
| **PK** |       id        |  INTEGER  |           Not Null            |
| **FK** |   website_id    |  VARCHAR  | Not Null - Website.website_id |
|        |   http_status   |  INTEGER  |           Not Null            |
|        | entry_timestamp | TIMESTAMP |           Not Null            |
|        |  response_time  |   FLOAT   |                               |
|        | regex_response  |   TEXT    |                               |

Each entry should be linked to a website, hence the relationship with Website table (1-n relationship).
After each request, a monitoring_entry is added, with its **http_status**, when was it sent **entry_timestamp**, and how long did it take to complete  **response_time**.
If a regex expression is provided, all pattern-matching answers are stored in **regex_response**

## Running the project

### Setup environment variables

Before running the project, you have to edit the .env file, with valid configuration.
Edit the .env file with your personal DB credentials

### Locally

Before running, make sure you have Python 3.8+ installed on your system.
Execute the following commands in the project directory

```shell
chmod +x run.sh # in case of missing execute permission
sh run.sh
```

The script will:

* Export env variables to the current session
* Create a virtual python env
* upgrade python package manager
* install requirements
* Run the python app

### Using Docker

For this method you need both [docker](https://www.docker.com/) and (
docker-compose)[https://docs.docker.com/compose] installed in your system.
To use a docker container to run the project, run the following cmd

```shell
docker-compose up
```

this will build the image, and run the app and expose it to the 8080 port (you can change the port in the docker-compose
file)

## Overview

When you start the app for the first time, it will initialize the database by creating Tables on the PostgresDB.
At startup, it will fetch existing jobs in the DB, and add them to the scheduler.
You can access the endpoints locally at [http://localhost:8080/docs](http://localhost:8080/docs#).

### Functionalities
1. **Get all jobs** : "Get /websites" with pagination
2. **Get a website with a specific keyword on its url** : "Get /website"
3. **Add a new website, hence a new job**: "Post /websites"
4. **Update an existing job**: "Put /websites"
5. **Get all monitoring data for a specific website using its url**: "Get /monitoring" with pagination

## Takeaways and improvement

This is application is a small poc of a monitoring tool that can be used for production grade application.
It was done thanks to the efforts of many developers who contribute to the open source community and discussions forums

### Things to improve
* General code quality tweaks
* Add some useful design patterns such as singleton for the database class
* Add more ways to access and manipulate data (other endpoints)
* Harness the asynchronous aspect of the app (use [aiohttp](https://docs.aiohttp.org/en/stable/)  to send requests, and build on it)
* A more complete test suit, here only the service tests are covered.