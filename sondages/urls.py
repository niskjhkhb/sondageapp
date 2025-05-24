from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create, name='create-survey'),
    path('survey/<int:pk>/', views.detail, name='survey-detail'),
    path('survey/<int:pk>/edit/', views.edit, name='survey-edit'),
    path('survey/<int:pk>/delete/', views.delete, name='survey-delete'),
    path('survey/<int:pk>/start/', views.start, name='survey-start'),
    path('survey/<int:survey_pk>/submit/<int:sub_pk>/', views.submit, name='survey-submit'),
    path('survey/<int:pk>/thanks/', views.thanks, name='survey-thanks'),
    path('survey/list/', views.survey_list, name='survey-list'),
]