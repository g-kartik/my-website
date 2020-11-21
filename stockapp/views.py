from django.shortcuts import render, redirect
from django.views import generic
import requests
import json
from .models import MyStocks
from .forms import StockForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

# Create your views here.


class Home(LoginRequiredMixin, generic.View):
    login_url = '/user-account/login/'

    def get(self, request):
        ticker_set = MyStocks.objects.all()
        tickers = ""
        for t in ticker_set:
            tickers += t.ticker + ","
        api_request = requests.get("https://cloud.iexapis.com/stable/stock/market/batch?symbols=" + tickers +
                                   "&types=quote&token=pk_e959396a8df04287a26278d566654f6e")
        try:
            stock_data = json.loads(api_request.content)
        except Exception:
            return render(request, 'stockapp/home.html', {'error': 'The API returned errors'})

        if 'error' in stock_data:
            messages.warning(request, "No stocks are available in the portfolio")
        return render(request, 'stockapp/home.html', {'stock_data': stock_data})

    def post(self, request):
        request.POST = request.POST.copy()
        request.POST['ticker'] = request.POST['ticker'].upper()
        api_request = requests.get("https://cloud.iexapis.com/stable/stock/" + request.POST['ticker'] +
                        "/quote?token=pk_e959396a8df04287a26278d566654f6e")
        if api_request.status_code == 404:
            messages.success(request, 'Unknown stock ticker symbol')
        else:
            form = StockForm(request.POST or None)
            if form.is_valid():
                form.save()
                messages.success(request, 'Stock Added Successfully')
        return redirect('stockapp:home')


@login_required(login_url='/user-account/login')
def remove_stock(request, ticker):
    stock = MyStocks.objects.get(ticker=ticker)
    stock.delete()
    messages.success(request, 'Stock removed successfully')
    return redirect('stockapp:home')

