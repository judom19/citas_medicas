from django.db import models
from django.utils import timezone

# Create your models here.
class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    
class Medico(models.Model):
    # Definir las opciones para los turnos
    TURNO_MANANA = 'Mañana'
    TURNO_TARDE = 'Tarde'
    OPCIONES_TURNO = [
        (TURNO_MANANA, 'Mañana'),
        (TURNO_TARDE, 'Tarde'),
    ]
    
    
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)
    horario = models.CharField(max_length=10, choices=OPCIONES_TURNO, default=TURNO_MANANA)
    inforamcion_contacto = models.CharField(max_length=100)
    
class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now)  
    
    
