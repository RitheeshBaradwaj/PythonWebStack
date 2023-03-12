#!/usr/bin/env python3
import os
import requests
import logging
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_FILE = BASE_DIR / "schema.sql"

API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "15SWOEC7H3CLW3B1")
SYMBOLS = ["IBM", "AAPL"]
DB_NAME = os.getenv("MYSQL_DATABASE", "financial")
USER = os.getenv("MYSQL_USER", "ritheesh")
PASSWORD = os.getenv("MYSQL_PASSWORD", "ritheeshPassword1")
HOST = os.getenv("HOST", "127.0.0.1")

# Set up logging
logging.basicConfig(
    filename="get_raw_data.log",
    filemode="w",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def get_financial_data(symbol):
    """
    Retrieve financial data for a given stock symbol from AlphaVantage API for the past two weeks.

    :param symbol: str, stock symbol to retrieve data for
    :return: list of dict, each dict contains financial data for a single day
    """
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()["Time Series (Daily)"]
        today = datetime.now().date()
        two_weeks_ago = today - timedelta(days=14)
        records = []
        for date, values in data.items():
            date = datetime.strptime(date, "%Y-%m-%d").date()
            if date >= two_weeks_ago and date <= today:
                record = {
                    "symbol": symbol,
                    "date": date.isoformat(),
                    "open_price": values["1. open"],
                    "close_price": values["4. close"],
                    "volume": values["6. volume"],
                }
                records.append(record)
        return records
    except requests.exceptions.RequestException as e:
        logging.error(
            f"Failed to retrieve financial data for symbol {symbol}: {str(e)}"
        )
        raise e
    except (ValueError, KeyError) as e:
        logging.error(f"Unexpected response format for symbol {symbol}: {str(e)}")
        raise e


def create_financial_data_table(conn):
    """
    Create a new table named 'financial_data' in the database with the specified connection.

    :param conn: mysql.connector.connection_cext.CMySQLConnection object, connection to the database
    :return: None
    """
    try:
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")
        with open(SCHEMA_FILE, "r") as f:
            schema = f.read()
        cursor.execute(schema, multi=True)
        conn.commit()
        logging.info("Created financial_data table")
    except mysql.connector.Error as e:
        logging.error(f"Failed to create financial_data table: {str(e)}")
        raise e
    except Exception as e:
        logging.error(f"Unknown error creating financial_data table: {e}")
        raise e


def insert_financial_data(conn, records, table_name="financial_data"):
    """
    Insert financial data records into the 'financial_data' table in the database with the specified connection.

    :param conn: mysql.connector.connection_cext.CMySQLConnection object, connection to the database
    :param records: list of dict, each dict contains financial data for a single day
    :return: None
    """
    try:
        cursor = conn.cursor()
        for record in records:
            cursor.execute(
                """
                INSERT INTO {} (symbol, date, open_price, close_price, volume)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE open_price=VALUES(open_price), close_price=VALUES(close_price), volume=VALUES(volume)
            """.format(
                    table_name
                ),
                (
                    record["symbol"],
                    record["date"],
                    record["open_price"],
                    record["close_price"],
                    record["volume"],
                ),
            )
        conn.commit()
        logging.info(
            f"Inserted {len(records)} financial data records for symbol {records[0]['symbol']}"
        )
        for record in records:
            logging.debug(record)
    except mysql.connector.Error as e:
        logging.error(f"Error inserting financial data into database: {str(e)}")
        conn.rollback()
    except Exception as e:
        logging.error(f"Unknown error inserting financial_data table: {e}")
        raise e


def main():
    """
    Main function that retrieves financial data for the specified stock symbols and inserts them into the database.

    :return: None
    """
    conn = None
    try:
        conn = mysql.connector.connect(user=USER, password=PASSWORD, host=HOST)
        create_financial_data_table(conn)
        for symbol in SYMBOLS:
            logging.info(f"Retrieving financial data for symbol {symbol}")
            records = get_financial_data(symbol)
            insert_financial_data(conn, records)
    except mysql.connector.Error as e:
        if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            logging.error("Something is wrong with your user name or password")
        elif e.errno == errorcode.ER_BAD_DB_ERROR:
            logging.error("Database does not exist")
        else:
            logging.error(f"Error connecting to database: {str(e)}")
        raise e
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
