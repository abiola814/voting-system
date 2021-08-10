from django.urls import path
from . import views

app_name = "vote"

urlpatterns = [
    path('add/', views.polls_add, name='add'),
    path('list/', views.polls_list, name='list'),
    path('<int:poll_id>/vote/', views.poll_vote, name='vote'),
     path('<int:poll_id>/', views.poll_detail, name='detail'),
     path('result/', views.result, name='result'),
       path('edit/<int:poll_id>/choice/add/', views.add_choice, name='add_choice'),
    path('edit/choice/<int:choice_id>/', views.choice_edit, name='choice_edit'),
    path('delete/choice/<int:choice_id>/', views.choice_delete, name='choice_delete'),
     path('edit/<int:poll_id>/', views.polls_edit, name='edit'),
    path('delete/<int:poll_id>/', views.polls_delete, name='delete_poll'),
    path('end/', views.endpoll, name='end_poll'),
]
