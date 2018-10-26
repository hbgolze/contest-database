"""contestdatabase URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include,url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

import django.contrib.auth.views
import randomtest.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
#    url(r'^accounts/login/$',randomtest.views.LoginView.as_view(), name='login'),
    url(r'^accounts/login/$',django.contrib.auth.views.login, name='login'),
    url(r'^accounts/logout/$', django.contrib.auth.views.logout, name='logout', kwargs={'next_page': '/'}),
    url(r'^accounts/change-password/$', randomtest.views.UpdatePassword, name='change_password'),
    url(r'^accounts/change-password-done/$', django.contrib.auth.views.password_change_done, name='password_change_done'),
    url(r'', include('randomtest.urls')),
    url(r'problemeditor/', include('problemeditor.urls')),
    url(r'^contestcollections/', include('contestcollections.urls')),
    url(r'^problemgroups/', include('groups.urls')),
    url(r'^asycompile/', include('asycompile.urls')),
    url(r'^search/', include('search.urls')),
#    url(r'^handouts/', include('handouts.urls')),
    url(r'^teacher/', include('teacher.urls')),
    url(r'^student/', include('student.urls')),
    url(r'^results/', include('results.urls')),
]
if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
