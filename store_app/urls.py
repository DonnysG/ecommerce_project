from django.urls import path
from . import views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('register/', views.registerPage, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('customer/<str:pk>/', views.customer, name="customer"),
    path('adminpanel/', views.adminPanel, name="adminpanel"),
    path('about/', views.About, name="about"),
    path('detail/<str:pk>/', views.product_view, name="product_view"),



    path('', views.store, name="store"),
    path('user/', views.userPage, name="user-page"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),

    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),

]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
