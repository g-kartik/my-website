from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.views.generic import View
from django.contrib import messages
from .forms import MySignUpForm, MyEditProfileForm, MyPasswordChangeForm
from django.contrib.auth.models import AnonymousUser


class LoginUser(View):
    def get(self, request):
        context = {'app_template': request.resolver_match.url_name + "/base.html"}
        return render(request, 'user_account/login.html', context=context)

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('mysite:home')
        else:
            messages.success(request, 'Your username and password did not match. Please try again')
            return redirect('user_account:login')


class LogoutUser(View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
            messages.success(request, 'You are now logged out')
        return redirect('mysite:home')


class SignUpUser(View):
    def get(self, request):
        form = MySignUpForm()
        return render(request, 'user_account/signup.html', {'form': form})

    def post(self, request):
        form = MySignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Registered Successfully")
            return redirect('todo:home')
        else:
            messages.success(request, "Your form has errors")
            return render(request, 'user_account/signup.html', {'form': form})


class EditProfile(View):
    def get(self, request):
        form = MyEditProfileForm(instance=request.user)
        return render(request, 'user_account/edit_profile.html', {'form': form})

    def post(self, request):
        form = MyEditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile edited successfully')
            return redirect('todo:home')
        else:
            messages.success(request, 'Form has errors')
            return render(request, 'user_account/edit_profile.html', {'form': form})


class ChangePassword(View):
    def get(self, request):
        form = MyPasswordChangeForm(user=request.user)
        return render(request, 'user_account/change_password.html', {'form': form})

    def post(self, request):
        form = MyPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Password changed successfully')
            return redirect('todo:home')
        else:
            messages.success(request, 'Form has errors')
            return render(request, 'user_account/change_password.html', {'form': form})


class GuestLogin(View):
    def get(self, request):
        login(request, AnonymousUser)
        messages.success(request, 'You are now logged in as a guest user')
        return redirect(request.path)

