from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from .models import ToDoItems
from django.contrib.auth.mixins import LoginRequiredMixin


class Home(LoginRequiredMixin, View):
    login_url = '/user-account/login'
    redirect_field_name = '/todo'

    def get(self, request):
        if request.user.is_authenticated:
            todo_list = ToDoItems.objects.filter(user=request.user)
            return render(request, 'todo/home.html', {'todo_list': todo_list})
        else:
            return render(request, 'todo/home.html')

    def post(self, request):
        if request.user.is_authenticated:
            todo_item = request.POST['todo_item']
            ToDoItems.objects.create(item_name=todo_item, user=request.user)
            return redirect('todo:home')


class EditItem(View):
    def get(self, request, item_id):
        if request.user.is_authenticated:
            item = ToDoItems.objects.get(pk=item_id, user=request.user)
            return render(request, 'todo/edit_item.html', {'item': item})

    def post(self, request, item_id):
        if request.user.is_authenticated:
            item = ToDoItems.objects.get(pk=item_id, user=request.user)
            new_name = request.POST['new_name']
            item.item_name = new_name
            item.save()
            messages.success(request, 'Item edited successfully')
            return redirect('todo:home')


def delete_item(request, item_id):
    if request.user.is_authenticated:
        item = ToDoItems.objects.get(pk=item_id, user=request.user)
        item.delete()
        messages.success(request, 'Item removed successfully')
        return redirect('todo:home')


def mark_item(request, item_id):
    item = ToDoItems.objects.get(pk=item_id)
    item.is_completed = not item.is_completed
    item.save()
    return redirect('todo:home')








