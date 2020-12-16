from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Search(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    requests_last_min = models.IntegerField(default=0)
    requests_last_day = models.IntegerField(default=0)
    hour_count = models.DateTimeField(auto_now_add=True)
    min_count = models.DateTimeField(auto_now_add=True)

    def get_or_set_permission(self):
        """
        Records the number of API calls made by the users and provides authorization of API requests
        :return dict: status: True if API requests didn't exceed the limit of 5/min and 100/day, otherwise False,
        request_last_min: Numbers of requests in last 1 minute, request_last_day: Number of requests in last 24 hours
        """
        current_time = timezone.now()
        permission = self.hour_permission(current_time, self.hour_count, self.min_count)
        return {'status': permission, 'request_last_min': self.requests_last_min,
                'request_last_day': self.requests_last_day}

    def minute_permission(self, current_time, min_count):
        """
        :param current_time: Current time of type datetime.datetime
        :param min_count: datetime.datetime object for counting minute limit
        :return: True if number of API requests made in past 60 seconds is less than 5
        """
        if (current_time - min_count).total_seconds() < 60:
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
        """
        :param current_time: Current time of type datetime.datetime
        :param hour_count: datetime.datetime object for counting hour limit
        :param min_count: datetime.datetime object for counting minute limit
        :return: True if number of API requests made in past 60 seconds is less than 5 and
        in past 24 hours is less than 100
        """
        if (current_time - hour_count).total_seconds() < 24*60*60:
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








