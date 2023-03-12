#!/usr/bin/env python3
import unittest
import mysql.connector

from unittest import mock
from unittest.mock import patch, MagicMock
from pathlib import Path
from get_raw_data import (
    get_financial_data,
    create_financial_data_table,
    insert_financial_data,
    main,
    SYMBOLS,
)

BASE_DIR = Path(__file__).resolve().parent
DB_NAME = "financial"
SCHEMA_FILE = BASE_DIR / "schema.sql"
SYMBOL = "AAPL"


class TestGetFinancialData(unittest.TestCase):
    @patch("requests.get")
    def test_positive(self, mock_get):
        # Arrange
        # simulate a successful API response
        mock_response = {
            "Time Series (Daily)": {
                "2023-03-10": {
                    "1. open": "123.45",
                    "4. close": "124.56",
                    "6. volume": "7890123",
                },
                "2023-03-09": {
                    "1. open": "122.34",
                    "4. close": "123.45",
                    "6. volume": "6789012",
                },
            }
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None

        # Act
        result = get_financial_data("AAPL")

        # Assert
        # check that the result is as expected
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["symbol"], "AAPL")
        self.assertEqual(result[0]["open_price"], "123.45")
        self.assertEqual(result[0]["close_price"], "124.56")
        self.assertEqual(result[0]["volume"], "7890123")
        self.assertEqual(result[1]["symbol"], "AAPL")
        self.assertEqual(result[1]["open_price"], "122.34")
        self.assertEqual(result[1]["close_price"], "123.45")
        self.assertEqual(result[1]["volume"], "6789012")

    @patch("requests.get")
    def test_api_error(self, mock_get):
        # Arrange
        # simulate an API error
        mock_get.return_value.raise_for_status.side_effect = Exception("API error")

        # Act & Assert
        # call the function and check that it raises an exception
        with self.assertRaises(Exception):
            get_financial_data("AAPL")

    @patch("requests.get")
    def test_response_format_error(self, mock_get):
        # Arrange
        # simulate an unexpected API response format
        mock_response = {"unexpected key": "unexpected value"}
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None

        # Act & Assert
        # call the function and check that it raises an exception
        with self.assertRaises(Exception):
            get_financial_data("AAPL")


class TestCreateFinancialDataTable2(unittest.TestCase):
    @patch("mysql.connector")
    def test_create_financial_data_table_positive(self, mock_connector):
        # Arrange
        # Setup mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connector.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Act
        create_financial_data_table(mock_conn)

        # Assert
        self.assertEqual(mock_cursor.execute.call_count, 3)
        mock_cursor.execute.assert_any_call(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        mock_cursor.execute.assert_any_call(f"USE {DB_NAME}")
        mock_cursor.execute.assert_any_call(mock.ANY, multi=True)
        mock_conn.commit.assert_called_once()

    @patch("mysql.connector")
    def test_create_financial_data_table_negative(self, mock_connector):
        # Arrange
        # Setup mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connector.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Raise an exception when execute is called on cursor
        mock_cursor.execute.side_effect = Exception("Test exception")

        # Act
        # Call function and expect it to raise an exception
        with self.assertRaises(Exception):
            create_financial_data_table(mock_conn)

        # Assert
        # Assert that necessary database calls were made
        self.assertEqual(mock_cursor.execute.call_count, 1)
        mock_cursor.execute.assert_any_call(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")


class TestInsertFinancialData(unittest.TestCase):
    @patch("mysql.connector")
    def test_insert_successful(self, mock_connector):
        # Arrange
        # Setup mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connector.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Define test input
        records = [
            {
                "symbol": "AAPL",
                "date": "2022-03-10",
                "open_price": 200.0,
                "close_price": 205.0,
                "volume": 1000000,
            },
            {
                "symbol": "AAPL",
                "date": "2022-03-09",
                "open_price": 198.0,
                "close_price": 202.0,
                "volume": 900000,
            },
        ]

        # Act
        insert_financial_data(mock_conn, records)

        # Assert
        self.assertEqual(mock_cursor.execute.call_count, len(records))
        self.assertTrue(mock_conn.cursor.called)
        self.assertEqual(mock_conn.commit.call_count, 1)

    @patch("mysql.connector")
    def test_insert_failed(self, mock_connector):
        # Arrange
        # Setup mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connector.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.execute.side_effect = Exception("Test exception")

        records = [
            {
                "symbol": "AAPL",
                "date": "2022-03-10",
                "open_price": 174.80,
                "close_price": 175.95,
                "volume": 30843130,
            },
            {
                "symbol": "AAPL",
                "date": "2022-03-09",
                "open_price": 173.60,
                "close_price": 174.14,
                "volume": 26804000,
            },
        ]

        # Act
        with self.assertRaises(Exception):
            insert_financial_data(mock_conn, records)

        # Assert
        self.assertTrue(mock_conn.cursor.called)
        self.assertFalse(mock_conn.commit.called)

    @patch.object(mysql.connector, "connect")
    def test_insert_sql_error(self, mock_connect):
        # Arrange
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = mysql.connector.Error()
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_conn = mock_connect.return_value
        records = [
            {
                "symbol": "AAPL",
                "date": "2022-03-10",
                "open_price": 100.0,
                "close_price": 101.0,
                "volume": 1000000,
            }
        ]

        # Act
        insert_financial_data(mock_conn, records)

        # Assert
        mock_conn.rollback.assert_called_once()


class TestMain(unittest.TestCase):
    @patch("mysql.connector.connect")
    @patch("get_raw_data.create_financial_data_table")
    @patch("get_raw_data.get_financial_data")
    @patch("get_raw_data.insert_financial_data")
    def test_main(
        self,
        mock_insert_financial_data,
        mock_get_financial_data,
        mock_create_financial_data_table,
        mock_mysql_connector_connect,
    ):
        # Arrange
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_mysql_connector_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock get_financial_data to return a list of two records
        mock_get_financial_data.return_value = [
            {
                "symbol": SYMBOL,
                "date": "2023-03-11",
                "open_price": 100,
                "close_price": 110,
                "volume": 10000,
            },
            {
                "symbol": SYMBOL,
                "date": "2023-03-12",
                "open_price": 110,
                "close_price": 120,
                "volume": 15000,
            },
        ]

        # Act
        main()

        # Assert
        # Check that create_financial_data_table was called with the correct argument
        mock_create_financial_data_table.assert_called_once_with(mock_conn)

        # Check that get_financial_data was called once for each symbol
        mock_get_financial_data.assert_has_calls(
            [mock.call(symbol) for symbol in SYMBOLS]
        )

        # Check that insert_financial_data was called twice with the correct arguments
        mock_insert_financial_data.assert_has_calls(
            mock_conn,
            [
                MagicMock(records=[mock_get_financial_data.return_value[0]]),
                MagicMock(records=[mock_get_financial_data.return_value[1]]),
            ],
        )


if __name__ == "__main__":
    unittest.main()
