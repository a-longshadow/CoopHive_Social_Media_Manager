from django.shortcuts import render

def dashboard(request):
    return render(request, 'bluesky/dashboard.html')
