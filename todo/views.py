from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib import messages
from .models import ToDoItems
from django.contrib.auth.mixins import LoginRequiredMixin
from  django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404


class Home(View):

    def get(self, request):
        todo_list = get_query_or_404(request, ToDoItems)
        return render(request, 'todo/home.html', {'todo_list': todo_list})

    def post(self, request):
        if request.user.is_authenticated:
            todo_item = request.POST['todo_item']
            create_object(request, ToDoItems, item_name=todo_item)
            return redirect('todo:home')


class EditItem(LoginRequiredMixin, View):
    login_url = '/user-account/login'

    def get(self, request, item_id):
        item = get_object_or_404(ToDoItems, pk=item_id, user=request.user)
        return render(request, 'todo/edit_item.html', {'item': item})

    def post(self, request, item_id):
        item = get_object_or_404(ToDoItems, pk=item_id, user=request.user)
        new_name = request.POST['new_name']
        item.item_name = new_name
        item.save()
        messages.success(request, 'Item edited successfully')
        return redirect('todo:home')


@login_required(login_url='/user-account/login')
def delete_item(request, item_id):
    item = get_object_or_404(ToDoItems, pk=item_id, user=request.user)
    item.delete()
    messages.success(request, 'Item removed successfully')
    return redirect('todo:home')


@login_required(login_url='/user-account/login')
def mark_item(request, item_id):
    item = get_object_or_404(ToDoItems, pk=item_id)
    item.is_completed = not item.is_completed
    item.save()
    return redirect('todo:home')


def get_query_or_404(request, model, **kwargs):
    """

    :param request:
    :param model:
    :param kwargs:
    :return:
    """
    def query_set_modify():
        """

        :param request:
        :param query_set:
        :param auth_query_set:
        :return:
        """
        for query in query_set:
            query.user = request.user
            query.save()
        return query_set

    session_id = request.session.get('session_id', None)
    if session_id is not None:
        try:
            query_set = model.objects.filter(session_id=session_id, **kwargs)
        except ObjectDoesNotExist:
            query_set = Http404
        else:

            # The user has recently logged in and has session data
            if request.user.is_authenticated:
                try:

                    # try and else: Wants to associate his session data with his login user data
                    # except: There is no login user data
                    auth_query_set = model.objects.filter(user=request.user, **kwargs)

                except ObjectDoesNotExist:
                    for query in query_set:
                        query.user = request.user
                        query.save()

                else:
                    query_set = query_set_modify()

                finally:

                    # delete session data for the login user
                    for query in query_set:
                        query.session_id = None
                        query.save()
                    del request.session['session_id']

    # The user is logged in and has no session data
    elif request.user.is_authenticated:
        try:
            query_set = model.objects.filter(user=request.user, **kwargs)
        except ObjectDoesNotExist:
            query_set = Http404
    else:
        query_set = [create_object(request, model, **kwargs)]
    return query_set


def create_object(request, model, **kwargs):
    session_id = request.session.get('session_id', None)
    if session_id is not None:
        obj = model.objects.create(session_id=session_id, **kwargs)
    else:
        obj = model.objects.create(**kwargs)
    return obj





