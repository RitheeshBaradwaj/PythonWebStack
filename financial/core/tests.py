from rest_framework import status
from rest_framework.test import APIClient

from .models import FinancialDataModel
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from unittest.mock import Mock, patch
from datetime import datetime, timedelta


class FinancialDataModelTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.start_date = datetime(2022, 1, 1).strftime("%Y-%m-%d")
        self.end_date = datetime(2022, 1, 31).strftime("%Y-%m-%d")
        self.symbol = "AAPL"
        self.url = reverse("statistics")

    def test_get_statistics_api_view(self):
        # Arrange
        # Create a mock queryset for the FinancialDataModel
        queryset_mock = Mock()
        queryset_mock.filter.return_value = queryset_mock
        queryset_mock.aggregate.return_value = {
            "open_price__avg": 100.0,
            "close_price__avg": 110.0,
            "volume__sum": 1000000,
        }

        # Patch the FinancialDataModel.objects.filter method to return the mock queryset
        with patch.object(
            FinancialDataModel.objects, "filter", return_value=queryset_mock
        ):
            # Act
            # Make a GET request to the StatisticsAPIView
            response = self.client.get(
                self.url,
                {
                    "start_date": self.start_date,
                    "end_date": self.end_date,
                    "symbol": self.symbol,
                },
                format="json",
            )

        # Assert
        # Check that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the response data matches the expected data
        expected_data = {
            "data": {
                "start_date": datetime.strptime(self.start_date, "%Y-%m-%d"),
                "end_date": datetime.strptime(self.end_date, "%Y-%m-%d"),
                "symbol": self.symbol,
                "average_daily_open_price": 100.0,
                "average_daily_close_price": 110.0,
                "average_daily_volume": 1000000,
            },
            "info": {"error": ""},
        }
        self.assertEqual(response.data, expected_data)

    def test_get_statistics_api_view_missing_parameters(self):
        # Arrange & Act
        # Make a GET request to the StatisticsAPIView with missing parameters
        response = self.client.get(self.url, {}, format="json")

        # Assert
        # Check that the response status code is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that the response data matches the expected data
        expected_data = {
            "data": {},
            "info": {
                "error": "start_date, end_date, and symbol are required parameters"
            },
        }
        self.assertEqual(response.data, expected_data)

    def test_get_statistics_api_view_invalid_date_format(self):
        # Arrange & Act
        # Make a GET request to the StatisticsAPIView with invalid date format
        response = self.client.get(
            self.url,
            {
                "start_date": "2022-01-01",
                "end_date": "2022/01/31",
                "symbol": self.symbol,
            },
            format="json",
        )

        # Assert
        # Check that the response status code is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that the response data matches the expected data
        expected_data = {
            "data": {},
            "info": {
                "error": "start_date and end_date must be in the format YYYY-MM-DD"
            },
        }
        self.assertEqual(response.data, expected_data)

    def test_get_statistics_api_view_invalid_start_end_date(self):
        # Arrange & Act
        # Make a GET request to the StatisticsAPIView with invalid date format
        response = self.client.get(
            self.url,
            {
                "start_date": "2022-01-01",
                "end_date": "2021-01-01",
                "symbol": self.symbol,
            },
            format="json",
        )

        # Assert
        # Check that the response status code is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that the response data matches the expected data
        expected_data = {
            "data": {},
            "info": {"error": "start_date must be before end_date"},
        }
        self.assertEqual(response.data, expected_data)

    @patch("core.models.FinancialDataModel.objects.filter")
    def test_filter_queryset_by_required_parameters(self, mock_filter):
        # Arrange
        # Test that the view filters the queryset by the required parameters
        start_date = (timezone.now() - timedelta(days=2)).date().strftime("%Y-%m-%d")
        end_date = timezone.now().date().strftime("%Y-%m-%d")
        symbol = "TEST1"

        mock_filter.return_value = FinancialDataModel.objects.none()

        # Act
        # Make a GET request to the StatisticsAPIView
        response = self.client.get(
            self.url, {"start_date": start_date, "end_date": end_date, "symbol": symbol}
        )

        # Act
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 6)
        self.assertIsNone(response.data["data"]["average_daily_open_price"])
        self.assertIsNone(response.data["data"]["average_daily_close_price"])
        self.assertIsNone(response.data["data"]["average_daily_volume"])


from django.test import TestCase, RequestFactory
from unittest.mock import patch, Mock
from unittest import mock
from datetime import datetime
from rest_framework import status

from .views import FinancialDataAPIView
from .serializers import FinancialDataSerializer
from .models import FinancialDataModel
from django.http import HttpRequest
from django.http import QueryDict


class FinancialDataAPIViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = FinancialDataAPIView.as_view()
        self.serializer_class = FinancialDataSerializer
        self.queryset = FinancialDataModel.objects.none()
        self.url = reverse("financial_data")
        self.financial_data = FinancialDataModel.objects.create(
            date="2022-01-01",
            symbol="AAPL",
            open_price=100.0,
            close_price=95.0,
            volume=1000000,
        )

    def test_get_queryset_symbol(self):
        # Arrange
        request = HttpRequest()
        request.query_params = QueryDict("symbol=AAPL")
        expected_queryset = FinancialDataModel.objects.filter(symbol="AAPL")

        # Act
        view = FinancialDataAPIView()
        actual_queryset = view.get_queryset(request)

        # Assert
        self.maxDiff = None
        self.assertEqual(
            actual_queryset.query.__str__(), expected_queryset.query.__str__()
        )

    def test_get_queryset_symbol_start_date(self):
        # Arrange
        request = HttpRequest()
        request.query_params = {"symbol": "AAPL", "start_date": "2022-01-01"}
        expected_queryset = FinancialDataModel.objects.filter(
            symbol="AAPL", date__gte=datetime.strptime("2022-01-01", "%Y-%m-%d")
        )

        # Act
        view = FinancialDataAPIView()
        actual_queryset = view.get_queryset(request)

        # Assert
        self.maxDiff = None
        self.assertEqual(
            actual_queryset.query.__str__(), expected_queryset.query.__str__()
        )

    def test_get_queryset(self):
        # Arrange
        request = HttpRequest()
        request.query_params = {
            "symbol": "AAPL",
            "start_date": "2022-01-01",
            "end_date": "2023-01-01",
        }
        expected_queryset = FinancialDataModel.objects.filter(
            symbol="AAPL",
            date__gte=datetime.strptime("2022-01-01", "%Y-%m-%d"),
            date__lte=datetime.strptime("2023-01-01", "%Y-%m-%d"),
        )

        # Act
        view = FinancialDataAPIView()
        actual_queryset = view.get_queryset(request)

        # Assert
        self.maxDiff = None
        self.assertEqual(
            actual_queryset.query.__str__(), expected_queryset.query.__str__()
        )

    def test_get_queryset_no_data(self):
        # Arrange
        request = HttpRequest()
        request.query_params = {}
        expected_queryset = FinancialDataModel.objects.filter()

        # Act
        view = FinancialDataAPIView()
        actual_queryset = view.get_queryset(request)

        # Assert
        self.maxDiff = None
        self.assertEqual(
            actual_queryset.query.__str__(), expected_queryset.query.__str__()
        )

    def test_get_queryset_invalid_data(self):
        # Arrange
        request = HttpRequest()
        request.query_params = {"invalid_key": "test message"}
        expected_queryset = FinancialDataModel.objects.filter()

        # Act
        view = FinancialDataAPIView()
        actual_queryset = view.get_queryset(request)

        # Assert
        self.maxDiff = None
        self.assertEqual(
            actual_queryset.query.__str__(), expected_queryset.query.__str__()
        )

    def test_get_without_filters(self):
        # Arrange
        request = HttpRequest()
        request.query_params = {}
        request.method = "GET"
        expected_data = {
            "data": [],
            "pagination": {"count": 0, "page": 1, "limit": 5, "pages": 1},
            "info": {"error": ""},
        }

        # Mock the queryset returned by get_queryset()
        with mock.patch.object(
            FinancialDataAPIView, "get_queryset"
        ) as mock_get_queryset:
            mock_get_queryset.return_value = self.queryset

            # Act
            view = FinancialDataAPIView()
            response = view.get(request)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_get_invalid_start_date(self):
        # Arrange
        request = HttpRequest()
        request.query_params = {"symbol": "AAPL", "start_date": "invalid_date"}
        request.method = "GET"
        expected_data = {
            "data": [],
            "pagination": {},
            "info": {"error": "start_date must be in the format YYYY-MM-DD"},
        }

        view = FinancialDataAPIView()

        # Act
        response = view.get(request)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)

    def test_get_invalid_end_date(self):
        # Arrange
        request = HttpRequest()
        request.query_params = {"symbol": "AAPL", "end_date": "invalid_date"}
        request.method = "GET"
        expected_data = {
            "data": [],
            "pagination": {},
            "info": {"error": "end_date must be in the format YYYY-MM-DD"},
        }

        view = FinancialDataAPIView()

        # Acts
        response = view.get(request)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)

    def test_get_when_queryset_has_no_results(self):
        # Arrange
        serializer_mock = Mock(spec=FinancialDataSerializer)
        serializer_mock.data = []
        paginator_mock = Mock()
        paginator_mock.page_size = 0
        paginator_mock.page.paginator.num_pages = 0
        paginator_mock.page.number = 1
        paginator_mock.paginate_queryset.return_value = []
        request = self.factory.get("/api/financial_data")
        request.query_params = QueryDict()
        view = FinancialDataAPIView()
        view.get_queryset = Mock(return_value=FinancialDataModel.objects.none())
        view.pagination_class = Mock(return_value=paginator_mock)
        view.serializer_class = Mock(return_value=serializer_mock)

        # Act
        response = view.get(request)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "data": [],
                "pagination": {"count": 0, "page": 1, "limit": 5, "pages": 0},
                "info": {"error": ""},
            },
        )

    def test_get_returns_data_when_queryset_has_results(self):
        # Arrange
        queryset = Mock(spec=FinancialDataModel.objects.all())
        queryset.count.return_value = 2
        serializer_data = [{"foo": "bar"}, {"baz": "qux"}]
        serializer = Mock(spec=FinancialDataSerializer)
        serializer.data = serializer_data
        serializer.return_value = serializer
        paginator = Mock()
        paginator.page_size = 5
        paginator.paginate_queryset.return_value = serializer_data
        paginator.page.paginator.num_pages = 1
        paginator.page.number = 1
        request = self.factory.get("/api/financial_data", {"limit": 5})
        request.query_params = QueryDict()
        view = FinancialDataAPIView()
        view.get_queryset = Mock(return_value=queryset)
        view.serializer_class = Mock(return_value=serializer)
        view.pagination_class = Mock(return_value=paginator)

        # Act
        response = view.get(request)

        # Assert
        view.get_queryset.assert_called_once_with(request)
        view.serializer_class.assert_called_once_with(serializer_data, many=True)
        view.pagination_class.assert_called_once_with()
        paginator.paginate_queryset.assert_called_once_with(queryset, request)
        self.assertEqual(
            response.data,
            {
                "data": serializer_data,
                "pagination": {"count": 2, "page": 1, "limit": 5, "pages": 1},
                "info": {"error": ""},
            },
        )
        self.assertEqual(response.status_code, 200)

    @patch("core.views.FinancialDataAPIView.get_queryset")
    def test_get(self, queryset_mock):
        queryset_mock.return_value = FinancialDataModel.objects.filter(symbol="AAPL")
        response = self.client.get(self.url, {"symbol": "AAPL"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"][0]["symbol"], "AAPL")
        self.assertEqual(response.data["pagination"]["count"], 1)
        self.assertEqual(response.data["pagination"]["page"], 1)
        self.assertEqual(response.data["pagination"]["limit"], 5)
        self.assertEqual(response.data["pagination"]["pages"], 1)

    @patch("core.views.FinancialDataAPIView.get_queryset")
    def test_get_invalid_symbol(self, queryset_mock):
        symbol = "invalid_symbol"
        queryset_mock.return_value = FinancialDataModel.objects.filter(symbol=symbol)
        response = self.client.get(self.url, {"symbol": symbol})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 0)
        self.assertEqual(response.data["pagination"]["count"], 0)
        self.assertEqual(response.data["pagination"]["page"], 1)
        self.assertEqual(response.data["pagination"]["limit"], 5)
        self.assertEqual(response.data["pagination"]["pages"], 1)
