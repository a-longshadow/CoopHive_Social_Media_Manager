from django.shortcuts import render
from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError
from django.core.cache import cache

def home(request):
    return render(request, 'core/home.html')

def health_check(request):
    """
    Basic health check endpoint that verifies:
    1. Database connection
    2. Cache connection (if configured)
    """
    health_status = {
        'status': 'healthy',
        'database': True,
        'cache': True,
        'errors': []
    }
    
    # Check database
    try:
        connections['default'].cursor()
    except OperationalError:
        health_status['database'] = False
        health_status['status'] = 'unhealthy'
        health_status['errors'].append('Database connection failed')
    
    # Check cache
    try:
        cache.set('health_check', 'ok', 1)
        if cache.get('health_check') != 'ok':
            raise Exception('Cache not working')
    except Exception:
        health_status['cache'] = False
        health_status['status'] = 'unhealthy'
        health_status['errors'].append('Cache connection failed')
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)
