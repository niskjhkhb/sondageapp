from django.urls import path
from . import views
from django.views.generic import TemplateView


urlpatterns = [
path('my-surveys/', views.my_surveys, name='my-surveys'),
path('survey-analytics/', views.survey_analytics, name='survey-analytics'),
path('survey-responses/', views.survey_responses, name='survey-responses'),
path('dashboard/', views.dashboard, name='dashboard'),
path('<int:sondage_id>/add_question', views.add_question, name='add_question'),
path('create_sondage/', views.create_sondage, name='create_sondage'),
path('<int:sondage_id>/participer/', views.participer_sondage, name='participer_sondage'),
path('merci/', TemplateView.as_view(template_name="sondages/merci.html"), name='merci'),



]

