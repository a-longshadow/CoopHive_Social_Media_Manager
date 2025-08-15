from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    """Bluesky dashboard view."""
    return render(request, 'bluesky/dashboard.html', {
        'platform': 'Bluesky',
        'platform_icon': '🦋',
        'platform_color': '#00bcd4'
    })
