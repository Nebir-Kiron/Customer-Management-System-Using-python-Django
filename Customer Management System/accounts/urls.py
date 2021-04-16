from django.urls import path
from . import views

urlpatterns = [
    path("login/",views.login_page, name='login'),
    path("logout/",views.logoutUser, name='logout'),
    path("register/",views.register_page, name='register'),


    path("",views.home, name='home'),
    path("user/",views.user_page, name='userpage'),
    path("product/",views.product, name='product'),
    path("customer/<str:pk_test>/",views.customer, name='customer'),


    path("account/",views.accounts_settings, name='account_settings'),


    path("create_order/<str:pk_create>/",views.create_order, name='create_order'),
    path("update_order/<slug:pk_order>/",views.update_order, name='update_order'),
    path("delete_order/<slug:pk_del>/",views.delete_order, name='delete_order'),

]


