from django.urls import path
from . import views
from .views import *

#namespace para acceder a las urls de la aplicacion 'citas_app'
app_name = 'citas_app'

urlpatterns = [
    path('user_registration/', UserRegisterView.as_view(), name='user_registration_view'), 
    path('full_user_registration/', CompletePatientRecordView.as_view(), name='full_patient_registration_view'), 
    path('appointments_index/', appointments_index, name='appointments_index'),    
    path('patients_index/',patients_index, name='patients_index'),
    path('contact_index/',contact_index, name='contact_index'), 
    path('appointments_list/', CitaMedicaListView.as_view(), name='appointments_list'),
    path('closest_appointments/', closest_appointments, name='closest_appointments'),
    path('appointments_create/', CitaMedicaCreateView, name='appointments_create'),
    path('appointments_update/<int:pk>/', CitaMedicaUpdateView.as_view(), name='appointments_update'),
    path('appointments_delete/<int:pk>/', CitaMedicaDeleteView.as_view(), name='appointments_delete'),  
    path('doctors_index/',doctors_index, name='doctors_index'),
    path('doctors_list/', MedicoListView, name='doctors_list'),
    path('doctors_create/', views.MedicoCreateView, name='doctors_create'),
    path('vista_solicitudes_medico/', vista_solicitudes_medico, name='vista_solicitudes_medico'),
    path('doctors_update/<int:pk>/', MedicoUpdateView, name='doctors_update'),
    path('doctors_delete/<int:pk>/', MedicoDeleteView, name='doctors_delete'),
    path('appointments_index_profile_edit/', EditarPerfilPacienteView.as_view(), name='appointments_index_profile_edit'),  
    path('citas_confirmadas_calendar/', CitasConfirmadasCalendar.as_view(), name='citas_confirmadas_calendar'),
    path('confirmar_cita_medico/<int:cita_id>/', confirmar_cita_medico, name='confirmar_cita_medico'),
    path('obtener_eventos/', obtener_eventos, name='obtener_eventos'),
    path('completar_cita/<int:cita_id>/', views.completar_cita, name='completar_cita'),
    path('ver_historial/<int:cita_id>/', ver_historial, name='ver_historial'),
    path('ver_historial_completo/<int:paciente_id>/',ver_historial_completo, name='ver_historial_completo'),
    path('reprogramar-cita/<int:cita_id>/', views.reprogramar_cita, name='reprogramar_cita'),
    path('historial_completo_paciente/', historial_completo_paciente, name='historial_completo_paciente'),
    path('specialties_index/', EspecialidadesView, name='specialties_index'),
    path('citas_generales/', citas_generales, name='citas_generales'),
    path('ver_historial_personal/<int:cita_id>/', ver_historial_personal, name='ver_historial_personal'),
    ]
