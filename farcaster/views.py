from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def dashboard(request):
    """Farcaster dashboard view."""
    return render(request, 'farcaster/dashboard.html', {
        'platform': 'Farcaster',
        'platform_icon': '⚡',
        'platform_color': '#8a63d2'
    })

# Placeholder views for URL patterns
@login_required
def cast_list(request):
    return HttpResponse("Farcaster casts - Coming soon!")

@login_required
def cast_create(request):
    return HttpResponse("Create Farcaster cast - Coming soon!")

@login_required
def cast_detail(request, pk):
    return HttpResponse(f"Farcaster cast {pk} - Coming soon!")

@login_required
def cast_edit(request, pk):
    return HttpResponse(f"Edit Farcaster cast {pk} - Coming soon!")

@login_required
def cast_delete(request, pk):
    return HttpResponse(f"Delete Farcaster cast {pk} - Coming soon!")

@login_required
def media_upload(request):
    return HttpResponse("Farcaster media upload - Coming soon!")

@login_required
def media_delete(request, pk):
    return HttpResponse(f"Delete Farcaster media {pk} - Coming soon!")

@login_required
def generate_preview(request):
    return HttpResponse("Farcaster preview - Coming soon!")

@login_required
def schedule_cast(request):
    return HttpResponse("Schedule Farcaster cast - Coming soon!")

@login_required
def publish_cast(request):
    return HttpResponse("Publish Farcaster cast - Coming soon!")

@login_required
def analytics(request):
    return HttpResponse("Farcaster analytics - Coming soon!")

@login_required
def export_analytics(request):
    return HttpResponse("Export Farcaster analytics - Coming soon!")
