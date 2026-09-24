from django.urls import path
from . import views

app_name = 'parenting'

urlpatterns = [
    path('', views.parenting_home, name='home'),
    path('add-child/', views.add_child, name='add_child'),
    path('child/<int:pk>/', views.child_detail, name='child_detail'),
    path('child/<int:pk>/pairing-code/', views.generate_pairing, name='generate_pairing'),
]
