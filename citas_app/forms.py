from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Medico, CitaMedica, Paciente, CompletarHistorial

#formualio a renderizar del modelo CitaMedica
class CitaMedicaForm(forms.ModelForm):
    class Meta:
        #modelo a utilizar
        model = CitaMedica
        #se excluye el campo paciente para que no sea visible en el formulario
        exclude = ['paciente']

#formulario a renderizar de la clase UserCreationForm para registrar un usuario
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        #modelo a utilizar
        model = User
        #campos a mostrar
        fields = ['username', 'password1', 'password2']
    #se personalizan los campos
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Usuario'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar'

#formulario a renderizar del modelo MedicoForm
class MedicoForm(forms.ModelForm):
    class Meta:
        #modelo a utilizar
        model = Medico
        #campos a mostrar
        fields = ['nombre_medico', 'apellido_medico', 'especialidad_medico']

    #se personalizan los campos   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre_medico'].label = 'Nombre'
        self.fields['apellido_medico'].label = 'Apellido'
        self.fields['especialidad_medico'].label = 'Especialidad'

    #se vincula el formulario de creacion de usuario para que se muestre junto con
    #el formulario actual
    usuario_medico = CustomUserCreationForm()

#formulario a renderizar del modelo PacienteForm    
class PacienteForm(forms.ModelForm):
    class Meta:
        #modelo a utilizar
        model = Paciente
        #campos a mostrar
        fields = ['nombre_paciente', 'apellido_paciente', 'edad_paciente', 'sexo_paciente', 'fecha_nac_paciente']

#formualio a renderizar basado en ModelForm
class CompletarHistorialForm(forms.ModelForm):
    #se define el campo 'completada' como campo booleano requerido
    completada = forms.BooleanField(
        required=True, 
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),  
    )

    class Meta:
        model = CompletarHistorial
        fields = ['diagnostico', 'tratamiento', 'completada']
        
#formulario a renderizar del modelo ReprogramarCitaForm
class ReprogramarCitaForm(forms.ModelForm):
    class Meta:
        #modelo a utilizar
        model = CitaMedica
        #excluyendo campos para no mostrarlos en el formulario
        exclude = ['paciente','medico']