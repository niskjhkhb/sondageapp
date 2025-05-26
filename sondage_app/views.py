from django.http import HttpResponse
from django.shortcuts import render, redirect 



#homepage view
def home(request):
    return render(request, 'base.html')
