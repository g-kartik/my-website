from django.db import models
from datetime import datetime, date, timedelta

# Create your models here.


class SearchRequest(models.Model):
    requests_last_min = models.IntegerField(default=0)
    requests_last_day = models.IntegerField(default=0)
    hour_count = models.TimeField(auto_now_add=True)
    min_count = models.TimeField(auto_now_add=True)

    def request_permission(self):
        current_time = datetime.combine(date.min, datetime.now().time())
        hour_count = datetime.combine(date.min, self.hour_count)
        min_count = datetime.combine(date.min, self.min_count)
        permission = self.hour_permission(current_time, hour_count, min_count)
        return {'status': permission, 'request_last_min': self.requests_last_min,
                'request_last_day': self.requests_last_day}

    def minute_permission(self, current_time, min_count):
        if current_time - min_count < timedelta(seconds=60):
            if self.requests_last_min < 5:
                self.requests_last_min += 1
                self.save()
                return True
            else:
                return False
        else:
            self.min_count = current_time
            self.requests_last_min = 1
            self.save()
            return True

    def hour_permission(self, current_time, hour_count, min_count):
        if current_time - hour_count < timedelta(hours=24):
            if self.requests_last_day < 100 and self.minute_permission(current_time, min_count):
                self.requests_last_day += 1
                self.save()
                return True
            else:
                return False
        else:
            self.hour_count = current_time
            self.min_count = current_time
            self.requests_last_day = 1
            self.requests_last_min = 1
            self.save()
            return True








