"""
URL configuration for coophive project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Configure Debug Toolbar URLS
if settings.DEBUG:
    import debug_toolbar

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Custom authentication URLs (prioritized over allauth)
    path('accounts/', include('user_account_manager.urls', namespace='accounts')),
    
    # Allauth URLs (for Google OAuth and other social auth)
    path('accounts/', include('allauth.urls')),
    
    # Homepage and core functionality
    path('', include('core.urls')),
    
    # Platform-specific URLs
    path('twitter/', include('twitter.urls')),
    path('linkedin/', include('linkedin.urls')),
    path('farcaster/', include('farcaster.urls')),
    path('bluesky/', include('bluesky.urls')),
]

# Add debug toolbar and media URLs in development
if settings.DEBUG:
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
