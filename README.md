# Financial Data Retrieval Application

![Python](https://img.shields.io/badge/Python-3.8-blue?style=flat&logo=python)
![Django](https://img.shields.io/badge/Django-4.1-green?style=flat&logo=django)
![MySQL](https://img.shields.io/badge/MySQL-8.0.32-blue?style=flat&logo=mysql)
![Docker](https://img.shields.io/badge/Docker-20.10.9-blue?style=flat&logo=docker)
![REST API](https://img.shields.io/badge/REST%20API-Django%20REST%20Framework-green)


`Financial Data API` project is a simple REST API built using Django Rest Framework that provides financial data to users. The API allows users to retrieve financial data of two stocks (IBM, Apple Inc.) for the most recently two weeks. The data is sourced from the [AlphaVantage](https://www.alphavantage.co/documentation/) API, which requires an API key to access the data. The API provides endpoints for retrieving raw data as well as endpoints for retrieving pre-processed data.

[GitHub Page](https://ritheeshbaradwaj.github.io/python_assignment/)

## Status

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)

[![Build and Publish Docker Image](https://github.com/RitheeshBaradwaj/python_assignment/actions/workflows/publish-docker-image.yaml/badge.svg?branch=main)](https://github.com/RitheeshBaradwaj/python_assignment/actions/workflows/publish-docker-image.yaml)

[![Test Financial Data APIs](https://github.com/RitheeshBaradwaj/python_assignment/actions/workflows/test-financial-data.yaml/badge.svg?branch=main)](https://github.com/RitheeshBaradwaj/python_assignment/actions/workflows/test-financial-data.yaml)

[![Test Web & Db Servers](https://github.com/RitheeshBaradwaj/python_assignment/actions/workflows/test-web-db-server.yaml/badge.svg?branch=main)](https://github.com/RitheeshBaradwaj/python_assignment/actions/workflows/test-web-db-server.yaml)

[Docker Image: financial-web](https://hub.docker.com/r/ritheeshbaradwaj/financial-web)

## Tech Stack

The tech stack used in this project is as follows:

- Python 3.8: A high-level programming language commonly used for web development and data analysis
- Django 4.1: Django is a high-level Python web framework that enables rapid development of secure and maintainable websites
- Django Rest Framework 3.4: A web framework for building RESTful APIs with Django, a Python-based web framework
- MySQL 8.0.32: An open-source relational database management system (RDBMS) that is commonly used for web applications
- Docker: A containerization platform that allows for the easy creation, deployment, and management of applications in containers.

## Installation Guide

### Prerequisites

- [Python 3.8.x](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)
- [Docker](https://docs.docker.com/engine/install/)
- [MySQL](https://ubuntu.com/server/docs/databases-mysql)

### Install Docker

You can install Docker using the following commands:

```bash
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io -y
```

### Install Docker Compose

You can install Docker Compose using pip:

```bash
sudo apt-get update
sudo apt-get install python3-pip -y
pip3 install docker-compose
```

### Start Docker

Start the Docker daemon using the following command:

```bash
sudo service docker start
```

## Run Financal Data API With Docker Compose

1. Clone the repository:

```bash
git clone https://github.com/RitheeshBaradwaj/python_assignment.git
```

2. Install all prerequisites mentioned above (Python3, Docker).

3. Navigate to the cloned repository directory.

```bash
cd python_assignment
```

4. Create a virtual environment.

```bash
python3 -m venv financial_env
```

5. Activate the virtual environment.

```bash
source financial_env/bin/activate
```

6. Install the required packages using pip.

```shell
pip install -r requirements.txt
```

7. For local developement, set all the env variables in `.env`

8. Start mysql server and django server with docker-compose

```bash
docker-compose up -d
```

Now, both web server and database servers are running, we need to populate the database `financial` with financial data
taken from AlphaVantage API.

## Maintaining the API Key

- In a development environment, you can store the API key as an environment variable, set `ALPHAVANTAGE_API_KEY` env var in `.env` file.

- In a production environment, you should store the API key as a secure environment variable on your server (eg: GitHub secrity keys). You can claim a [free API](https://www.alphavantage.co/support/#api-key).

For workflows, I stored the secerets here: [GitHub secerets](https://github.com/RitheeshBaradwaj/python_assignment/settings/secrets/actions)

Run `get_raw_data.py` to populate the database with data from IBM, AAPL.

```bash
python get_raw_data.py
```

## API Usage

Once our database has some records and we can retrive them.

The project provides the following APIs:

- `/api/financial_data/`: Returns a list of financial data records.
- `/api/statistics/`: Returns statistics for financial data records.

### /api/financial_data

This API returns a list of financial data based on the given parameters.

#### Request

The following parameters are supported:

- `start_date`: The start date for the financial data (optional).
- `end_date`: The end date for the financial data (optional).
- `symbol`: The stock symbol for the financial data (optional).
- `limit`: The number of items to return per page (optional).
- `page`: The page number to return (optional).

#### Example request:

```bash
curl -X GET 'http://localhost:5000/api/financial_data?start_date=2023-01-01&end_date=2023-01-14&symbol=IBM&limit=3&page=2'
```

#### Response

The response will be a JSON object with the following keys:

- `data`: An array of financial data objects.
- `pagination`: An object containing pagination information.
- `info`: An object containing additional information about the request, such as error messages.

#### Example response:

```bash
{
    "data": [
        {
            "symbol": "IBM",
            "date": "2023-01-05",
            "open_price": "153.08",
            "close_price": "154.52",
            "volume": "62199013",
        },
        {
            "symbol": "IBM",
            "date": "2023-01-06",
            "open_price": "153.08",
            "close_price": "154.52",
            "volume": "59099013"
        },
        {
            "symbol": "IBM",
            "date": "2023-01-09",
            "open_price": "153.08",
            "close_price": "154.52",
            "volume": "42399013"
        }
    ],
    "pagination": {
        "count": 20,
        "page": 2,
        "limit": 3,
        "pages": 7
    },
    "info": {'error': ''}
}
```

### /api/statistics

This API returns statistics for the financial data based on the given parameters.

#### Request

The following parameters are supported:

- `start_date`: The start date for the financial data (required).
- `end_date`: The end date for the financial data (required).
- `symbol`: The stock symbol for the financial data (required).

#### Example request

```bash
curl -X GET 'http://localhost:5000/api/statistics?start_date=2023-01-01&end_date=2023-01-31&symbol=IBM'
```

#### Response

The response will be a JSON object with the following keys:

- `data`: An object containing statistics information.
- `info`: An object containing additional information about the request, such as error messages.

#### Example response

```bash
{
    "data": {
        "start_date": "2023-01-01",
        "end_date": "2023-01-31",
        "symbol": "IBM",
        "average_daily_open_price": 123.45,
        "average_daily_close_price": 234.56,
        "average_daily_volume": 1000000
    },
    "info": {'error': ''}
}
```

## Run Database And Web Server on Local Environment

To run the database and webserver locally, you can follow below steps

### Run Django

1. Install dependencies

```bash
pip install -r requirements.txt
``

2. Run the migrations

```bash
python financial/manage.py makemigrations
python financial/manage.py migrate
```

3. Start the server at requried port

```bash
python financial/manage.py runserver 0.0.0.0:5000
```

### Run MySQL

1. Install mysql server

```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo systemctl start mysql
sudo systemctl status mysql
```

2. To secure the installation, run the following command:

```bash
sudo mysql_secure_installation
```
This will guide you through a series of prompts to secure your installation.

You can then log in to the MySQL server using the following command:

```bash
sudo mysql -u root -p
```

Enter the root password you set during installation.

To create a new database, use the following command:

```bash
CREATE DATABASE dbname;
```

Replace "dbname" with the name you want to give your database. For our application we use `financial`.

To create a new user and grant permissions to the database, use the following commands:

```bash
CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON dbname.* TO 'username'@'localhost';
```

Replace "username" with the name you want to give your user and "password" with the password you want to use.

## Running Tests

To run tests for this project, follow these steps:

1. Ensure that all the necessary dependencies are installed by running the command pip install -r requirements.txt

### Getting Raw Data

1. Execute the following command to run unit tests for `get_raw_data.py`

```bash
python -m unittest tests/test_get_raw_data.py
``

2. To test `get_raw_data.py with sql server. Start the test database and execute following command

```bash
python -m unittest tests/test_get_raw_data.py
```

### Django Tests For APIs

1. Run the following command to run migrations for test database

```bash
export TEST_DATABASE=ON
python financial/manage.py makemigrations
python financial/manage.py migrate
```

2. Run the tests for `core` app

```bash
python financial/manage.py test core.tests
```

The tests will run and output the results to the console. Any failures or errors will also be displayed along with the traceback for easy debugging.

## How to Check the Published Docker Image

I have used GitHub Actions to publish the latest docker image to Docker Hub.
To check the published Docker image, you can run the following command in your terminal after logging into Docker Hub:

Image link: https://hub.docker.com/r/ritheeshbaradwaj/financial-web

```bash
docker pull ritheeshbaradwaj/financial-web
```

To verify that the image has been pulled successfully, you can run the following command:

```bash
docker images
```

This will display a list of all the images you have downloaded to your machine. Check if the image you just downloaded is listed there.

## How to Check the GitHub Workflows

To check the GitHub Workflows, follow these steps:

1. Click on the "Actions" tab
2. Here you can see a list of workflows that have been set up in this repository

- `Test Financial Data APIs`: To test `get_raw_data.py` and django `financial/core` apis
- `Build and Publish Docker Image`: To build and publish latest docker image to Docker Hub

## Contact Information

I appreciate your interest in `Financial Data Retrieval APIs`. You can reach to me through the following channels:

- Email: ritheeshbaradwaj@gmail.com
- LinkedIn: [ritheesh-baradwaj-yellenki](https://www.linkedin.com/in/ritheesh-baradwaj-yellenki/)
- [GitHub Issues](https://github.com/RitheeshBaradwaj/python_assignment/issues)

## Thank you :D
