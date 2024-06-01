# urls.py
from django.urls import path
from .views import (login_view, logout_view,personal_cabinet_view,
                    register,patients,profile_pat, add_manual_data,clear_patient_data,
                    plot_patient_data,plot_page,
                    clear_patient_data_last_day)
from django.urls import path, include
from .views import PatientDataList







urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('personal_cabinet/', personal_cabinet_view, name='personal_cabinet'),
    path('register/', register, name='register'),
    path('patients/', patients, name='patients'),
    path('patient/<int:user_id>/', profile_pat, name='profile_pat'),
    path('api/patientdata/', PatientDataList.as_view(), name='patientdata-list'),
    path('add_manual_data/<int:user_id>/', add_manual_data, name='add_manual_data'),
    path('clear_patient_data/<int:user_id>/', clear_patient_data, name='clear_patient_data'),
    path('clear_patient_data_last_day/<int:user_id>/', clear_patient_data_last_day, name='clear_patient_data_last_day'),
    path('plot_patient_data/<int:user_id>/', plot_patient_data, name='plot_patient_data'),
    path('plot_page/<int:user_id>/', plot_page, name='plot_page'),

]
