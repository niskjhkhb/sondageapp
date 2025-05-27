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
path('<uuid:sondage_id>/participer/', views.participer_sondage, name='participer_sondage'),
path('merci/', TemplateView.as_view(template_name="sondages/merci.html"), name='merci'),
path('/QCU/', views.QCU, name='QCU'),
path('/TEXT/', views.TEXT, name='TEXT'),
path('/SCALE/', views.SCALE, name='SCALE'),
path('/QCM/', views.QCM, name='QCM'),
path('/mixed/', views.mixed, name='mixed'),
path('save_scale_sondage/', views.save_scale_sondage, name='save_scale_sondage'),  # Add this line
path('save_qcu_sondage/', views.save_qcu_sondage, name='save_qcu_sondage'),
path('save_qcm_sondage/', views.save_qcm_sondage, name='save_qcm_sondage'),  
path('save_text_sondage/', views.save_text_sondage, name='save_text_sondage'),  # Add this line
path('save_mixed_sondage/', views.save_mixed_sondage, name='save_mixed_sondage'),  # Add this line
path('<int:sondage_id>/details/', views.survey_details, name='survey_details'),
path('<int:sondage_id>/update/', views.update_sondage, name='update_sondage'),
path('<int:sondage_id>/delete/', views.delete_sondage, name='delete_sondage'),
path('<int:sondage_id>/export/csv/', views.export_responses, name='export_responses'),
path('<int:sondage_id>/export/excel/', views.export_responses_excel, name='export_responses_excel'),
path('<int:sondage_id>/results/', views.survey_results, name='survey_results'),
    
]

