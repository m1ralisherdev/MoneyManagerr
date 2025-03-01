from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from .models import HistoryModel
from CardApp.models import CardModel
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated


class HistoryAdd(APIView):
    serializer_class = HistoryModelSerializer
    queryset = HistoryModel

    @swagger_auto_schema(request_body=HistoryModelSerializer)
    def post(self, request):
        card_related = int(request.data.get("card_related"))
        price = request.data.get("price")
        where = request.data.get("where")
        filtr_1 = CardModel.objects.filter(id=card_related).first()
        HistoryModel.objects.create(card_related=card_related, price=price, where=where)
        return Response({"Message": "History yaratildi"}, status=200)


class HistoryAdd1(APIView):
    serializer_class = HistoryModelSerializer
    queryset = HistoryModel

    def post(self, request):
        serializer = HistoryModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"Message": "History yaratildi"}, status=201)
        else:
            return Response(serializer.errors)


import datetime


class DayHistory(APIView):

    def get(self, request):
        day = datetime.datetime.now()
        day = day.strftime("%d")
        filtr1 = HistoryModel.objects.filter(when_date__day=26)
        for i in filtr1:
            print(i.when_date)
        return Response({'msg': "ok"})


class MonthHistory(APIView):
    def get(self, request):
        month = datetime.datetime.now()
        month = month.strftime("%m")
        print(month)
        filtr2 = HistoryModel.objects.filter(when_date__month=month)
        all_data = {}
        for i in filtr2:
            all_data[i.who_payed.username] = [i.when_date, i.card_related.card_number, i.where]
        return Response(all_data, status=200)


# class TopDayPayed(APIView):
#     def get(self, request):
#         day = datetime.datetime.now().day
#         try:
#             filtr1 = HistoryModel.objects.filter(when_date__day=day).order_by('-price').first()
#             if filtr1:
#                 serializer = HistoryModelSerializer1(filtr1)
#                 return Response(serializer.data, status=200)
#             else:
#                 return Response({"detail": "No data found for today"}, status=404)
#         except HistoryModel.DoesNotExist:
#             return Response({"detail": "No data found for today"}, status=404)

# return Response(serializer.data, status=200)
from celery.result import AsyncResult
from rest_framework.views import APIView
from rest_framework.response import Response
from PaymentApp.tasks import get_top_day_payed

class TopDayPayed(APIView):
    """
    API endpoint to trigger the Celery task for fetching the top-paid item of the day
    and to check the status/result of the task using its task ID.
    """

    def get(self, request, *args, **kwargs):
        """
        Trigger the Celery task asynchronously.
        If a task ID is provided via query parameter, return its status/result.
        """
        task_id = request.query_params.get("task_id")

        if task_id:
            # If task ID is provided, check the status of the task
            result = AsyncResult(task_id)
            response = {"task_id": task_id, "state": result.state}

            if result.state == "SUCCESS":
                response["result"] = result.result
                return Response(response, status=200)
            elif result.state == "FAILURE":
                response["error"] = str(result.result)
                return Response(response, status=500)
            else:
                return Response(response, status=202)
        else:
            # If no task ID is provided, trigger a new task
            task = get_top_day_payed.delay()
            return Response({"task_id": task.id}, status=202)

