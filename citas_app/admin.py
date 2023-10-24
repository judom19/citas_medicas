from django.contrib import admin
from .models import Paciente,Medico,CitaMedica, CompletarHistorial

#registro de los modelos en panel de administracion
admin.site.register(Paciente)
admin.site.register(Medico)
admin.site.register(CitaMedica)
admin.site.register(CompletarHistorial)
