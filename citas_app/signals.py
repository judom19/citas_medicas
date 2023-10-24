from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import Medico

@receiver(post_save, sender=Medico)
def agregar_a_grupo_medico(sender, instance, created, **kwargs):
    if created:
        #verifica si el grupo "Médicos" existe o créalo si no existe
        grupo_medico, created = Group.objects.get_or_create(name='Medico')

        #agrega el usuario médico al grupo "Medico"
        instance.usuario_medico.groups.add(grupo_medico)
