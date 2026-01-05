from django.shortcuts import render

def login(request):
    return render(request, 'piro_index/base.html')
