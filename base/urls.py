from django.conf import settings
from django.template.defaulttags import url
from django.urls import path
from django.views.static import serve

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup, name="signup"),
    path('signin', views.signin, name="signin"),
    path('signout', views.signout, name="signout"),
    path('lobby/', views.lobby),
    path('room/', views.room),
    path('get_token/', views.getToken),
    path('activate/<uidb64>/<token>', views.activate, name="activate"),

    path('create_member/', views.createMember),
    path('get_member/', views.getMember),
    path('delete_member/', views.deleteMember),

    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

