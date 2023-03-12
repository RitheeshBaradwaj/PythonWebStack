from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from django.db.models import Avg, Sum
from datetime import datetime

from .models import FinancialDataModel
from .serializers import FinancialDataSerializer


class FinancialDataAPIView(APIView):
    serializer_class = FinancialDataSerializer
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        try:
            # Get the queryset based on the filters provided in the request
            queryset = self.get_queryset(request)

            # Paginate the results
            paginator = self.pagination_class()
            paginator.page_size = request.query_params.get("limit", 5)
            result_page = paginator.paginate_queryset(queryset, request)
            serializer = self.serializer_class(result_page, many=True)

            # Construct the response data
            response_data = {
                "data": serializer.data,
                "pagination": {
                    "count": queryset.count(),
                    "page": paginator.page.number,
                    "limit": int(paginator.page_size),
                    "pages": paginator.page.paginator.num_pages,
                },
                "info": {"error": ""},
            }

            return Response(response_data)

        except Exception as e:
            # Return an error response if an exception is raised
            return Response(
                {"data": [], "pagination": {}, "info": {"error": str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_queryset(self, request):
        # Get all FinancialDataModel objects
        queryset = FinancialDataModel.objects.all()

        # Filter by start date if start_date parameter is provided in the request
        start_date = request.query_params.get("start_date")
        if start_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("start_date must be in the format YYYY-MM-DD")
            queryset = queryset.filter(date__gte=start_date)

        # Filter by end date if end_date parameter is provided in the request
        end_date = request.query_params.get("end_date")
        if end_date:
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("end_date must be in the format YYYY-MM-DD")
            queryset = queryset.filter(date__lte=end_date)

        # Filter by symbol if symbol parameter is provided in the request
        symbol = request.query_params.get("symbol")
        if symbol:
            queryset = queryset.filter(symbol=symbol)

        return queryset


class StatisticsAPIView(APIView):
    serializer_class = FinancialDataModel

    def get(self, request, *args, **kwargs):
        try:
            # Get the required parameters from the query params
            start_date = request.query_params.get("start_date")
            end_date = request.query_params.get("end_date")
            symbol = request.query_params.get("symbol")

            # Check if all required parameters are present
            if not all([start_date, end_date, symbol]):
                raise ValueError(
                    "start_date, end_date, and symbol are required parameters"
                )

            # Check if the start_date and end_date parameters are in the correct format
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError(
                    "start_date and end_date must be in the format YYYY-MM-DD"
                )

            # Check if the start_date parameter is before the end_date parameter
            if start_date > end_date:
                raise ValueError("start_date must be before end_date")

            # Get the queryset filtered by the required parameters
            queryset = FinancialDataModel.objects.filter(
                date__gte=start_date, date__lte=end_date, symbol=symbol
            )

            # Calculate the statistics
            average_daily_open_price = queryset.aggregate(Avg("open_price"))[
                "open_price__avg"
            ]
            average_daily_close_price = queryset.aggregate(Avg("close_price"))[
                "close_price__avg"
            ]
            average_daily_volume = queryset.aggregate(Sum("volume"))["volume__sum"]

            # Construct the response data
            response_data = {
                "data": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "symbol": symbol,
                    "average_daily_open_price": average_daily_open_price,
                    "average_daily_close_price": average_daily_close_price,
                    "average_daily_volume": average_daily_volume,
                },
                "info": {"error": ""},
            }

            return Response(response_data)

        except Exception as e:
            return Response(
                {"data": {}, "info": {"error": str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
