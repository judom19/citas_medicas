""" from schedule.models import Calendar

class CitasConfirmadasCalendar(Calendar):
    # Filtra los eventos para mostrar solo las citas confirmadas
    def get_events(self, start, end, **kwargs):
        events = super().get_events(start, end, **kwargs)
        return events.filter(cita__confirmado=True)
     """