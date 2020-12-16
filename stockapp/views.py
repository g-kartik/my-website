from django.shortcuts import render, redirect
from django.views.generic import View
import requests
import json
from .models import MyStocks
from django.contrib import messages
from mysite.models import get_query_object_or_404, get_query_set_or_404, create_object
from django.http import Http404


class Home(View):

    def get(self, request):
        try:
            ticker_set = get_query_set_or_404(request, MyStocks)
        except Http404:
            ticker_set = []
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
        ticker = request.POST['ticker'].upper()
        api_request = requests.get("https://cloud.iexapis.com/stable/stock/" + request.POST['ticker'] +
                        "/quote?token=pk_e959396a8df04287a26278d566654f6e")
        if api_request.status_code == 404:
            messages.success(request, 'Unknown stock ticker symbol')
        else:
            create_object(request, MyStocks, ticker=ticker)
            messages.success(request, 'Stock Added Successfully')
        return redirect('stockapp:home')


def remove_stock(request, ticker):
    stock = get_query_object_or_404(MyStocks, ticker=ticker)
    stock.delete()
    messages.success(request, 'Stock removed successfully')
    return redirect('stockapp:home')

