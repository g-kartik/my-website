from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.views.generic import View
from django.contrib import messages
from .forms import MySignUpForm, MyEditProfileForm, MyPasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class LoginUser(UserPassesTestMixin, View):
    def test_func(self):
        return not self.request.user.is_authenticated

    def get(self, request):
        return render(request, 'user_account/login.html')

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


class LogoutUser(LoginRequiredMixin, View):
    login_url = '/user-account/login'

    def get(self, request):
        logout(request)
        messages.success(request, 'You are now logged out')
        return redirect('mysite:home')


class SignUpUser(UserPassesTestMixin, View):
    def test_func(self):
        return not self.request.user.is_authenticated

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
            return redirect('mysite:home')
        else:
            messages.success(request, "Your form has errors")
            return render(request, 'user_account/signup.html', {'form': form})


class EditProfile(LoginRequiredMixin, View):
    login_url = '/user-account/login'

    def get(self, request):
        form = MyEditProfileForm(instance=request.user)
        return render(request, 'user_account/edit_profile.html', {'form': form})

    def post(self, request):
        form = MyEditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile edited successfully')
            return redirect('mysite:home')
        else:
            messages.success(request, 'Form has errors')
            return render(request, 'user_account/edit_profile.html', {'form': form})


class ChangePassword(LoginRequiredMixin, View):
    login_url = '/user-account/login'

    def get(self, request):
        form = MyPasswordChangeForm(user=request.user)
        return render(request, 'user_account/change_password.html', {'form': form})

    def post(self, request):
        form = MyPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Password changed successfully')
            return redirect('mysite:home')
        else:
            messages.success(request, 'Form has errors')
            return render(request, 'user_account/change_password.html', {'form': form})

