from django.apps import AppConfig

#conf para señal de asignacion de grupos
class CitasAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'citas_app'

    def ready(self):
        import citas_app.signals
