from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('add-ticket/', views.add_ticket, name='add_ticket'),
    path('reassign/<int:ticket_id>/', views.reassign_ticket, name='reassign_ticket'),
    path('auto-assign/', views.auto_assign_all, name='auto_assign_all'),
]
