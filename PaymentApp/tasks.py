from celery import shared_task
from datetime import datetime
from PaymentApp.models import HistoryModel
from PaymentApp.serializers import HistoryModelSerializer1


@shared_task
def get_top_day_payed():
    day = datetime.now().day
    try:
        # Get the first record for the current day ordered by price (descending)
        filtr1 = HistoryModel.objects.filter(when_date__day=day).order_by('-price').first()

        if filtr1:
            # Serialize the result and return it
            serializer = HistoryModelSerializer1(filtr1)
            return serializer.data
        else:
            # If no data found for today
            return {"detail": "No data found for today"}
    except Exception as e:
        # If any unexpected error occurs, log and return the error message
        return {"detail": str(e)}