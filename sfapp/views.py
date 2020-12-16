from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponseRedirect
from django.contrib import messages
import requests
import json
from django.core.cache import cache
from .models import Search
from django.utils.html import mark_safe
from django.core.exceptions import ObjectDoesNotExist


class Home(View):
    # Variable for storing API query string from the POST data of the search form
    api_query_string = ""
    cookie_test_passed = False

    def get(self, request, page=None):
        """
        Mainly it displays the search page for the Stack Overflow API. And when page is requested
        it can send GET request to the API or to the database cache for getting the response objects
        :param request: HTTP request object
        :param page: Page number of search paginator
        :return: Search form if page is None, else search form and search results according to page number and user
        permissions.
        :except: If API response has errors, return search form and error messages
        """
        if not request.session.session_key:
            Home.api_query_string = ""
            Home.cookie_test_passed = False

        # Check if browser passed cookie accept test
        if not Home.cookie_test_passed:
            cookie_test(request)

        context = {}

        # if search page is queried
        if page is not None and Home.cookie_test_passed:
            api_query = Home.api_query_string + f"&page={page}"

            # Try to get response from cache else query from API if user has permission
            query_response = cache.get(api_query)
            if query_response is not None:
                messages.success(request, "Request queried from cache")
            else:
                user_obj = self.get_user_obj(request)
                permission = self.has_permission(request, user_obj)
                if permission['status']:
                    query_response = self.request_from_api(request, api_query, permission)

            # if either of cache or api response has valid data
            if query_response is not None:
                context['search_data'] = query_response
                if query_response['has_more']:
                    context['next_page'] = page + 1
            if page != 1:
                context['previous_page'] = page - 1

        return render(request, 'sfapp/home.html', context=context)

    def post(self, request):
        """
        Extract non Null key-value pairs from the POST data of the search form as a string and assign it to the
        api_query_string class variable.
        :param request: HTTP request object
        :return: HTTP redirect response to page view
        """
        request_dict = request.POST.copy()
        del(request_dict['csrfmiddlewaretoken'])
        api_query_param = []
        for name, value in request_dict.items():
            if value != '':
                api_query_param.append(f"{name}={value}")
        Home.api_query_string = "&" + "&".join(api_query_param)
        return redirect('sfapp:page', page=1)

    def get_user_obj(self, request):
        """
        Get user object entry from Search table. It can either be an anonymous user or a authenticated user.
        If an authenticated user has previous session has data then that data is merged into the user entry in the
        database
        :param request: HTTP request object
        :return:User object from Search table
        """
        user_obj = None
        search_id = request.session.get('search_id', None)
        if search_id is not None:
            user_obj = Search.objects.get(pk=search_id)
            if request.user.is_authenticated:
                try:
                    auth_user_obj = Search.objects.get(user=request.user)
                except ObjectDoesNotExist:
                    user_obj.user = request.user
                    user_obj.save()
                else:
                    auth_user_obj.requests_last_min += user_obj.requests_last_min
                    auth_user_obj.requests_last_day += user_obj.requests_last_day
                    auth_user_obj.min_count = user_obj.min_count
                    auth_user_obj.save()
                    user_obj.delete()
                    return auth_user_obj
                finally:
                    del request.session['search_id']
        elif request.user.is_authenticated:
            try:
                user_obj = Search.objects.get(user=request.user)
            except ObjectDoesNotExist:
                pass
        else:
            user_obj = Search.objects.create()
            request.session['search_id'] = user_obj.pk
        return user_obj

    def has_permission(self, request, user_obj):
        """
        Gives permission for API requests for the user object. If number of requests in last 1 min exceed 5 or in last
        24 hours exceed 100 then permission status will be False otherwise True
        :param request: Http Request Object
        :param user_obj: User object
        :return: A dictionary of 1. Bool - Permission Status 2. Number of requests last minute and 3. Number of requests
        last 24 hours
        """
        permission = user_obj.get_or_set_permission()
        if not permission['status']:
            if permission['request_last_min'] >= 5:
                messages.success(request, "API requests limit exceeded for last minute. "
                                          "Try again after few seconds or search previous cached requests")
            elif permission['request_last_min'] >= 100:
                messages.success(request, "API requests limit exceeded for last 24 hours. "
                                          "Try again after few hours or search previous cached requests")
        return permission

    def request_from_api(self, request, api_query, permission):
        """
        Returns API response from Stack Overflow API as per the api_query
        :param request:HTTP user object
        :param api_query: API query string
        :param permission: Permission Dict
        :return: API query response
        """
        # try to get response from API
        end_point = "https://api.stackexchange.com/2.2/search/advanced?site=stackoverflow"
        query_response = requests.get(end_point + api_query)
        query_response = json.loads(query_response.content)

        # If errors, add error parameters to messages; else add query_response to cache
        if 'error_id' in query_response:
            messages.success(request, f"error_id={query_response['error_id']}\n"
                                      f"error_message{query_response['error_message']}\n"
                                      f"error_name{query_response['error_name']}")
            return None
        else:
            cache.set(api_query, query_response, 30 * 60)
            messages.success(request, "Request queried from API")
            messages.success(request, mark_safe(f"API requests last minute - {permission['request_last_min']}/ 5<br>"
                                                f"API requests last 24 hours - {permission['request_last_day']}/ 100"))
            return query_response


def cookie_test(request):
    """
    Test browser for accept cookies
    :param request:
    :return: None
    """
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
        Home.cookie_test_passed = True
    else:
        request.session.set_test_cookie()
        request.session.set_expiry(None)
        messages.success(request, "Please ensure your browser accepts cookies")
    return None


class Resume(View):
    def get(self, request):
        return HttpResponseRedirect("https://raw.githubusercontent.com/g-kartik/resume/main/G_Karthik_Resume.pdf")