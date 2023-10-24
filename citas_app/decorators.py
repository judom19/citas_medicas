from django.shortcuts import redirect
from django.contrib import messages

#metodo para verificar si el usuario pertenece al grupo Medico
def es_medico(user):
    return user.groups.filter(name='Medico').exists()

#metodo para verificar si el usuario pertenece al grupo Paciente
def es_paciente(user):
    return user.groups.filter(name='Paciente').exists()

#metodo para verificar si el usuario es un superusuario
def es_admin(user):
    return user.is_superuser

#otorga los permisos a los usuarios que pertenecen al grupo Medico
def permiso_medico(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if es_medico(request.user) or es_admin(request.user):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "No tienes permiso para acceder a esta vista.")
            return redirect('citas_app:appointments_index')
    return _wrapped_view

#otorga los permisos a los usuarios que pertenecen al grupo Paciente
def permiso_paciente(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if es_paciente(request.user) or es_admin(request.user):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "No tienes permiso para acceder a esta vista.")
            return redirect('citas_app:appointments_index')
    return _wrapped_view
