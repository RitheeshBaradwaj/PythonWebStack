#!/usr/bin/env python3
import unittest
import mysql.connector
import datetime

from decimal import Decimal
from unittest.mock import patch, mock_open
from pathlib import Path
from get_raw_data import (
    get_financial_data,
    create_financial_data_table,
    insert_financial_data,
)

SYMBOL = "AAPL"
BASE_DIR = Path(__file__).resolve().parent
SCHEMA_FILE = BASE_DIR / "tests" / "test_schema.sql"
DB_NAME = "financial"
TABLE_NAME = "test_financial_data"

USER = "ritheesh"
PASSWORD = "Mysql123"
HOST = "127.0.0.1"


class TestGetRawData(unittest.TestCase):
    def setUp(self):
        self.conn = mysql.connector.connect(user=USER, password=PASSWORD, host=HOST)
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"USE {DB_NAME}")

    def tearDown(self):
        self.cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
        self.conn.close()

    def test_get_financial_data(self):
        # Arrange & Act
        data = get_financial_data(SYMBOL)

        # Assert
        self.assertTrue(isinstance(data, list))
        if len(data) > 0:
            self.assertTrue(isinstance(data[0], dict))
            self.assertTrue("symbol" in data[0])
            self.assertTrue("date" in data[0])
            self.assertTrue("open_price" in data[0])
            self.assertTrue("close_price" in data[0])
            self.assertTrue("volume" in data[0])

    def test_get_financial_data_invalid_symbol(self):
        # Arrange, Act, Assert
        with self.assertRaises(KeyError):
            get_financial_data("INVALID_SYMBOL")

    def test_create_financial_data_table(self):
        # Arrange
        mock_schema_contents = """
            CREATE TABLE IF NOT EXISTS test_financial_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(255) NOT NULL,
            date DATE NOT NULL,
            open_price DECIMAL(10,2) NOT NULL,
            close_price DECIMAL(10,2) NOT NULL,
            volume BIGINT NOT NULL
            );
        """
        with patch(
            "builtins.open", mock_open(read_data=mock_schema_contents)
        ) as mock_file:
            # Act
            create_financial_data_table(self.conn)

        # Assert
        cursor = self.conn.cursor()
        cursor.execute(f"SHOW TABLES LIKE '{TABLE_NAME}'")
        table_exists = cursor.fetchone()
        self.assertIsNotNone(table_exists)

    def test_insert_financial_data(self):
        # Arrange
        records = [
            {
                "symbol": SYMBOL,
                "date": "2023-03-10",
                "open_price": "220.92",
                "close_price": "222.46",
                "volume": "29474759",
            },
            {
                "symbol": SYMBOL,
                "date": "2023-03-09",
                "open_price": "217.67",
                "close_price": "218.89",
                "volume": "39344709",
            },
        ]

        mock_schema_contents = """
            CREATE TABLE IF NOT EXISTS test_financial_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(255) NOT NULL,
            date DATE NOT NULL,
            open_price DECIMAL(10,2) NOT NULL,
            close_price DECIMAL(10,2) NOT NULL,
            volume BIGINT NOT NULL
            );
        """

        with patch(
            "builtins.open", mock_open(read_data=mock_schema_contents)
        ) as mock_file:
            # Act
            create_financial_data_table(self.conn)

        # Assert
        insert_financial_data(self.conn, records, TABLE_NAME)
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE symbol='AAPL'")
        inserted_records = cursor.fetchall()
        self.assertEqual(len(inserted_records), 2)

        expected_record_1 = (
            1,
            "AAPL",
            datetime.date(2023, 3, 10),
            Decimal("220.92").quantize(Decimal(".01")),
            Decimal("222.46").quantize(Decimal(".01")),
            29474759,
        )
        expected_record_2 = (
            2,
            SYMBOL,
            datetime.date(2023, 3, 9),
            Decimal("217.67").quantize(Decimal(".01")),
            Decimal("218.89").quantize(Decimal(".01")),
            39344709,
        )
        self.assertEqual(inserted_records[0], expected_record_1)
        self.assertEqual(inserted_records[1], expected_record_2)
