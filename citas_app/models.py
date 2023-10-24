from django.db import models
from django.contrib.auth.models import User

class Paciente(models.Model):
    
    """
    Modelo de paciente.
    Atributos:
    - usuario_paciente: Usuario para que el paciente agente su cita
    - nombre_paciente: Nombre del paciente.
    - apellido_paciente: Apellido del paciente.
    - edad_paciente: Edad del paciente.
    - sexo_paciente: Sexo del paciente.
    - fecha_nac_paciente: Fecha de nacimiento del paciente.
    """
    
    usuario_paciente = models.OneToOneField(User, on_delete=models.CASCADE, default=None )
    nombre_paciente = models.CharField(max_length=100, null=True)
    apellido_paciente = models.CharField(max_length=100)
    edad_paciente = models.PositiveIntegerField(default=0)
    sexo_paciente = models.CharField(max_length=10, null=True)
    fecha_nac_paciente = models.DateField(default=None)
    
    def __str__(self):
        return f"{self.nombre_paciente} {self.apellido_paciente}"
    
class Medico(models.Model):
    """
    Modelo de médico.
    Atributos:
    - nombre_medico: Nombre del médico.
    - apellido_medico: Apellido del médico.
    - especialidad_medico: Especialidad del médico.
    - usuario_medico: Usuario del médico para poder consultar las citas.
        
    """
    nombre_medico = models.CharField(max_length=100)
    apellido_medico = models.CharField(max_length=100)
    especialidad_medico = models.CharField(max_length=100)
    usuario_medico = models.OneToOneField(User, on_delete=models.CASCADE, related_name='medico')
        
    def __str__(self):
        return f"{self.nombre_medico}{self.apellido_medico}"
    
    
class CitaMedica(models.Model):
    """
    Modelo de cita médica.
    Atributos:
    - paciente: Paciente que tiene la cita.
    - medico: Médico que atiende la cita.
    - fecha: Fecha de la cita.
    - hora: Hora de la cita.
    - motivo: Motivo de la cita.
"""
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    fecha = models.DateField(default='2023-01-01')
    hora = models.TimeField(default='00:00')
    motivo = models.CharField(max_length=200)
    confirmado = models.BooleanField(default=False)
    completada = models.BooleanField(default=False)   
    def __str__(self):
        return f'Cita Médica #{self.id} - Paciente: {self.paciente.nombre_paciente}, Médico: {self.medico.nombre_medico}'



class CompletarHistorial(models.Model):
    """
    Modelo que representa el historial médico completo de una cita médica.
    Atributos:
    - cita_medica: La cita médica a la que se relaciona este historial.
    - paciente: El paciente relacionado con este historial.
    - fecha: La fecha de creación del historial (se autocompleta).
    - diagnostico: El diagnóstico del paciente para la cita médica.
    - tratamiento: El tratamiento recomendado para el paciente.
    """
    cita_medica = models.ForeignKey(CitaMedica, on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now=True)
    diagnostico = models.TextField()
    tratamiento = models.TextField()
    
    def __str__(self):
        return f"{self.cita_medica}"

