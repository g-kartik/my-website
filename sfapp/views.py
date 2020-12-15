from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponseRedirect
from django.contrib import messages
import requests
import json
from django.core.cache import cache
from .models import SearchRequest
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import mark_safe


class Home(View):
    login_url = '/user_account/login/'
    api_query_string = ""

    def get(self, request, page=None):
        context = {}

        # if search page is queried
        if page is not None:
            api_query = Home.api_query_string + f"&page={page}"

            # Try to get response from cache
            query_response = cache.get(api_query)

            if query_response is not None:
                messages.success(request, "Request queried from cache")
            else:
                # request permission
                try:
                    api_user_requests = SearchRequest.objects.get(pk=1)
                except ObjectDoesNotExist:
                    api_user_requests = SearchRequest.objects.create()

                permission = api_user_requests.request_permission()
                if not permission['status']:
                    if permission['request_last_min'] == 5:
                        messages.success(request, "API requests limit exceeded for last minute. "
                                                  "Try again after few seconds or search previous cached requests")
                    elif permission['request_last_min'] == 100:
                        messages.success(request, "API requests limit exceeded for last 24 hours. "
                                                  "Try again after few hours or search previous cached requests")
                else:
                    # try to get response from API
                    end_point = "https://api.stackexchange.com/2.2/search/advanced?site=stackoverflow"
                    query_response = requests.get(end_point + api_query)
                    query_response = json.loads(query_response.content)

                    # If errors add error parameters to messages; else add query_response to cache
                    if 'error_id' in query_response:
                        messages.success(request, f"error_id={query_response['error_id']}\n"
                                                  f"error_message{query_response['error_message']}\n"
                                                  f"error_name{query_response['error_name']}")
                        query_response = None
                    else:
                        cache.set(api_query, query_response, 30*60)
                        messages.success(request, "Request queried from API")
                        messages.success(request, mark_safe(f"API requests last minute - {permission['request_last_min']}/ 10<br>"
                                                  f"API requests last 24 hours - {permission['request_last_day']}/ 100"))

            # if either of cache or api response has valid data
            if query_response is not None:
                context['search_data'] = query_response
                if query_response['has_more']:
                    context['next_page'] = page + 1
            if page != 1:
                context['previous_page'] = page - 1
        return render(request, 'sfapp/home.html', context=context)

    def post(self, request):
        request_dict = request.POST.copy()
        del(request_dict['csrfmiddlewaretoken'])
        api_query_param = []
        for name, value in request_dict.items():
            if value != '':
                api_query_param.append(f"{name}={value}")
        Home.api_query_string = "&" + "&".join(api_query_param)
        return redirect('sfapp:page', page=1)


class Resume(View):
    def get(self, request):
        return HttpResponseRedirect("https://raw.githubusercontent.com/g-kartik/resume/main/G_Karthik_Resume.pdf")