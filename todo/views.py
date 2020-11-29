from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib import messages
from .models import ToDoItems
from django.contrib.auth.mixins import LoginRequiredMixin
from  django.contrib.auth.decorators import login_required


class Home(LoginRequiredMixin, View):
    login_url = '/user-account/login'

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








