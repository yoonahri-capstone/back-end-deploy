"""memsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, re_path, include
from rest_framework import routers

from django.conf import settings
from django.conf.urls.static import static

from memmem_app import views

router = routers.DefaultRouter()
router.register(r'user', views.MyUserViewSet)
#router.register(r'folder', views.FolderViewSet)
#router.register(r'scrap', views.ScrapViewSet)
#router.register(r'list', views.ListViewSet)
#router.register(r'scraps', views.TotalListViewSet)

urlpatterns = [
    path('memmem_app/', include('memmem_app.urls')),
    path('memmem_app/auth', include('knox.urls')),
    path('', include(router.urls)),
    re_path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
