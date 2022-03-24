from django.urls import path
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
]