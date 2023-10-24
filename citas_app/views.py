from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy,reverse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Paciente, Medico, CitaMedica, CompletarHistorial
from .forms import CitaMedicaForm, PacienteForm, MedicoForm, CitaMedicaForm, CustomUserCreationForm, CompletarHistorialForm, ReprogramarCitaForm
from schedule.models import Calendar, Event
from datetime import datetime, timedelta
from .decorators import permiso_medico

#vista encargada del registro inicial de usuario
class UserRegisterView(CreateView):        
    #template a renderizar 
    template_name = 'user_patient_register/user_register.html'
    
    #formulario base
    form_class = UserCreationForm
    
    #metodo de validacion de formulario e inicio de sesion
    def form_valid(self, form):        
        #respuesta al estar validado el formulario
        response = super().form_valid(form)
        
        #encriptando contraseña de usuario para almacenarla en la base de datos
        self.object.set_password(form.cleaned_data['password1'])
        
        #guardando objeto
        self.object.save()
        
        #iniciando sesion de forma automatica
        login(self.request, self.object)
        
        #devolviendo la respuesta
        return response
    
    #metodo para redireccionar la vista al ser validado el formulario
    def get_success_url(self):
        return reverse_lazy('citas_app:full_patient_registration_view')
    
    
#vista encargada de continuar el registro completo del paciente
@method_decorator(login_required, name='dispatch')
class CompletePatientRecordView(CreateView):    
    #template a renderizar
    template_name = 'user_patient_register/full_patient_registration.html'    
    
    #modelo base para renderizar el formulario
    model = Paciente    
    
    #campos a mostrar en el template
    fields = [
        'nombre_paciente',
        'apellido_paciente',
        'edad_paciente',
        'sexo_paciente',
        'fecha_nac_paciente',
    ]    
    
    #redireccion despues de validar el formulario
    success_url = reverse_lazy('citas_app:appointments_index')
    
    #metodo para validar el formulario y enviar informacion
    def form_valid(self, form):        
        #asociando el usuario de la sesion actual al campo usuario_paciente del formulario
        form.instance.usuario_paciente = self.request.user        
        
        #enviando informacion 
        return super().form_valid(form)

    
#vista encargada de editar el perfil del paciente
class EditarPerfilPacienteView(UpdateView):
    #modelo a utilizar
    model = Paciente
    
    #formualario a utilizar
    form_class = PacienteForm
    
    #template a renderizar
    template_name = 'user_patient_register/full_patient_registration_edit.html'
    
    #vista a redireccionar despues de editar con exito
    success_url = reverse_lazy('citas_app:appointments_index')

    #recuperando el perfil del paciente actual
    def get_object(self):
        return Paciente.objects.get(usuario_paciente=self.request.user)
    
#vista encargada de usuario no autenticado    
def no_login_view(request):
    
    context = {
        'mensaje': 'Gracias por visitarnos, inicia sesion para gestionar tus citas'
    }
    return render(request,'no_login.html', context)


#vista encargada de cerrar sesion de usuario
def custom_logout_view(request):
    logout(request)
    return redirect(reverse_lazy('login'))


#vista principal de medicos
@permiso_medico#permiso de autorizacion para medicos
def doctors_index(request):
    context = {
        'mensaje': 'Gestión de medicos'
    }
    return render(request,'doctors/doctors_index.html', context)


#vista principal de pacientes
@permiso_medico
def patients_index(request):
    pacientes = Paciente.objects.all()
    context = {
        'pacientes': pacientes,
        'mensaje': 'Gestión de pacientes'
    }
    return render(request, 'patients/patients_index.html', context)

#vista principal citas
@login_required
def appointments_index(request):
    user = request.user
    
    # inicializa las variables medico y paciente en None
    medico = None
    paciente = None

    # verifica si el usuario es un médico y obtiene el objeto de médico
    if hasattr(user, 'medico'):
        medico = user.medico
    
    # verifica si el usuario es un paciente y obtiene el objeto de paciente
    if hasattr(user, 'paciente'):
        paciente = user.paciente

    context = {
        'user': user,
        'medico': medico,
        'paciente': paciente,
    }
    return render(request, 'base.html', context)


#vista principal de contacto
@login_required
def contact_index(request):
    context = {
        'mensaje': 'Gestión de contacto'
    }
    return render(request,'contact/contact_index.html', context)

#vista encargada de crear la cita medica
def CitaMedicaCreateView(request):
    #se verifica que el usuario esté autenticado y sea un paciente
    if not request.user.is_authenticated or not hasattr(request.user, 'paciente'):
        return render(request, 'no_login.html', {'message': 'No tienes permiso para crear citas.'})
    
    #obteniendo los dias disponibles para mostrarse en el template de la vista actual
    dias_disponibles = obtener_dias_disponibles()
    
    #validacion del formulario
    if request.method == 'POST':
        form = CitaMedicaForm(request.POST)
        if form.is_valid():
            #se verifica si ya existe una cita para la fecha seleccionada
            fecha = form.cleaned_data['fecha']
            medico = form.cleaned_data['medico']

            #se comprueba si existe una cita con la misma fecha y se muestra un error en caso de ser asi
            if CitaMedica.objects.filter(fecha=fecha, medico=medico).exists():
                
                return render(request, 'CRUD_appointments/error.html', {'form': form, 'error_message': 'No hay mas espacios para esa fecha'})

            #se crea una instancia de CitaMedica pendiente de guardar
            cita_medica = form.save(commit=False)

            #se asigna el paciente (usuario de la sesión) a la cita medica
            cita_medica.paciente = request.user.paciente

            #se guarda la cita médica con el paciente asignado
            cita_medica.save()

            #se redirecciona a la vista asiganda en caso se der almacenada correctamente
            return redirect(reverse_lazy('medical_appointments:appointments_list'))
    
    #caso contrario se renderiza el formulario de nuevo
    else:
        form = CitaMedicaForm()

    #se rederiza el template pasandole el diccionario
    return render(request, 'CRUD_appointments/citas_medicas_create.html', {'form': form, 'dias_disponibles':dias_disponibles})


#vista encargada de mostrar la lista de citas del paciente
@method_decorator(login_required, name='dispatch')
class CitaMedicaListView(ListView):
    #modelo a utilizar
    model = CitaMedica
    
    #template a utilizar
    template_name = 'CRUD_appointments/citas_medicas_list.html'
    
    #nombre de referencia para acceder a los objetos 
    context_object_name = 'solicitudes_citas'

    #se filtran las citas medicas del paciente actualmente autenticado
    def get_queryset(self):
        return CitaMedica.objects.filter(paciente=self.request.user.paciente)
    
    #metodo para pasarle al contexto los dias disponibles del metodo obtener_dias_disponibles()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dias_disponibles'] = obtener_dias_disponibles()        
        return context

#vista encargada de actualizar la cita por parte del paciente
@method_decorator(login_required, name='dispatch') 
class CitaMedicaUpdateView(UpdateView):
    #modelos a utilizar
    model = CitaMedica
    
    #formulario a utilizar
    form_class = CitaMedicaForm
    
    #template a renderizar
    template_name = 'CRUD_appointments/citas_medicas_create.html'
    
    #nombre de referencia para acceder a los objetos 
    context_object_name = 'cita'
    
    #vista a redireccionar despues de editar con exito
    success_url = reverse_lazy('citas_app:appointments_list')
    
    #metodo para pasarle al contexto los dias disponibles del metodo obtener_dias_disponibles()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context['dias_disponibles'] = obtener_dias_disponibles()        
        return context
    

#vista encargada de eliminar una cita medica por parte del paciente
@method_decorator(login_required, name='dispatch') 
class CitaMedicaDeleteView(DeleteView):
    model = CitaMedica
    template_name = 'CRUD_appointments/citas_medicas_delete_confirm.html'
    context_object_name = 'cita'
    success_url = reverse_lazy('citas_app:appointments_list')
    
#metodo encargado de obtener las citas mas cercanas
def closest_appointments(request):
    #se obtiene la fecha y hora actual
    now = timezone.now()

    #se busca la cita medica mas cercana y confirmada
    proxima_cita = CitaMedica.objects.filter(
        paciente=request.user.paciente, #se filtra por el paciente actual
        fecha__gte=now,  #que la fecha sea mayor o igual a la actual
        confirmado=True, #que la cita este confirmada
        completada=False #que la cita aun no se encuentre completada
    ).order_by('fecha').first()#se ordenan las citas filtradas por fecha
    
    #se busca la cita medica mas cercana y solicitada
    proxima_cita_solicitada = CitaMedica.objects.filter(
        paciente=request.user.paciente,  #se filtra por el paciente actual
        fecha__gte=now,  #que la fecha sea mayor o igual a la actual
        confirmado=False,#que la cita no este confirmada
        completada=False #que la cita no este finalizada
    ).order_by('fecha').first()#se ordenan las citas filtradas por fecha
    
    #se pasan ambas consultas por el contexto
    context = {
        'proxima_cita': proxima_cita,
        'proxima_cita_solicitada':proxima_cita_solicitada,
    }
    
    #se renderiza el template con pasandole el contexto
    return render(request, 'CRUD_appointments/closest_appointments.html', context)


#vista encargada de listar los medicos
@permiso_medico
def MedicoListView(request):
    #se filtran los objetos medicos
    medicos = Medico.objects.all()
    
    #se pasan los objetos por contexto
    context = {'medicos': medicos}
    
    #se renderiza el template pasandole el contexto
    return render(request, 'doctors/doctors_list.html', context)


#vista encargada de crear medicos
@permiso_medico
def MedicoCreateView(request):
    #se valida el formualio
    if request.method == 'POST':
        #formulario a utilizar para los datos del medico
        medico_form = MedicoForm(request.POST)
        
        #formulario a utilizar para los datos de usuario del medico
        user_form = CustomUserCreationForm(request.POST)

        #si ambos formularios son validos
        if medico_form.is_valid() and user_form.is_valid():
            #se guarda el usuario
            nuevo_usuario = user_form.save()
            
            #se crea una instancia del medico y se deja pendiente de guardar
            nuevo_medico = medico_form.save(commit=False)
            
            #se asigna el usuario creado del formulario guardado al campo usuario_medico del objeto medico
            nuevo_medico.usuario_medico = nuevo_usuario
            
            #se guarda el medico 
            nuevo_medico.save()

            #se redirecciona a la vista de la lista de medicos
            return redirect(reverse_lazy('citas_app:doctors_list'))
    
    #caso contrario se renderizan los formularios vacios
    else:
        medico_form = MedicoForm()
        user_form = CustomUserCreationForm()

    #se renderiza el template que muestra los dos formularios
    return render(request, 'doctors/doctors_create.html', {'medico_form': medico_form, 'user_form': user_form})


#vista encargada de actualizar medicos
@permiso_medico
def MedicoUpdateView(request, pk):
    #template a renderizar
    template_name = 'doctors/doctors_update.html'

    #se obtiene el medico para editar
    medico = Medico.objects.get(pk=pk)

    if request.method == 'POST':
        #si la solicitud es POST se procesa el formulario
        medico_form = MedicoForm(request.POST, instance=medico)

        #si el formulario es valido
        if medico_form.is_valid():
            
            #se guardan los datos del formulario
            medico_form.save()
            
            #se redirecciona a la vista en caso de ser guardado correctamente
            return redirect(reverse_lazy('citas_app:doctors_list'))
        
    #caso contrario  se si la solicitud no es POST, muestra el formulario con los datos actuales del médico
    else:
        medico_form = MedicoForm(instance=medico)

    #se pasa el formualio por medio del contexto
    context = {'medico_form': medico_form}
    
    #se renderiza el template pasandole el contexto
    return render(request, template_name, context)


#vista encargada de eliminar medicos
@permiso_medico
def MedicoDeleteView(request, pk):
    #se obtiene el objeto Medico que se va a eliminar
    medico = Medico.objects.get(pk=pk)

    #template a renderizar
    template_name = 'doctors/doctors_delete.html'

    #vista a redireccionar en caso de eliminar al medico de manera exitosa
    success_url = reverse_lazy('citas_app:doctors_list')

    #si el metodo de la solicitud es POST
    if request.method == 'POST':
        #se elimina al medico
        medico.delete()

        #se redirige a la vista asignada en success_url
        return redirect(success_url)

    #se pasa todo por contexto
    context = {'medico': medico, 'success_url': success_url}

    #se renderiza el template pasandole el contexto
    return render(request, template_name, context)
    

#vista encargada de mostrar la lista de citas solicitadas a medicos
@permiso_medico
def vista_solicitudes_medico(request):
    #se obtiene el médico actualmente autenticado
    medico = request.user.medico

    #se recuperan todas las solicitudes de citas relacionadas con este médico
    solicitudes_citas = CitaMedica.objects.filter(medico=medico)

    #se obtienen los eventos de citas confirmadas
    eventos = obtener_eventos(request)

    #se renderiza el template pasando los objetos por diccionario
    return render(request, 'doctors/vista_solicitudes_medico.html', {'solicitudes_citas': solicitudes_citas, 'eventos': eventos})


#metodo encargado de obtener los metodos generados de la vista confirmar_cita_medico()
@permiso_medico
def obtener_eventos(request):
    #se obtiene el medico actualmente autenticado    
    medico = request.user.medico
    
    #se obtienen las citas médicas confirmadas relacionadas con este medico
    citas_confirmadas = CitaMedica.objects.filter(medico=medico, confirmado=True)

    #se convierten las citas confirmadas en eventos con formato JSON para poder pasarlos al calendario
    #se crea la lista que va a almacenar los eventos tipo JSON
    eventos = []
    
    #se recorren los objetos filtrados en citas_confirmadas
    for cita in citas_confirmadas:
        #se agregan las citas en la lista eventos y creando objeto tipo JSON
        eventos.append({
            'title': f'{cita.motivo}',
            'start': cita.fecha.isoformat(),
            'end': cita.fecha.isoformat(),
            # Agrega otros campos específicos de tus eventos aquí si los tienes
        })

    #se devuelven el objeto tipo JSON con los valores de las citas confirmadas almacenadas dentro
    return eventos

#vista encargada de confirmar la cita y generar lso eventos del calendario
@permiso_medico
def confirmar_cita_medico(request, cita_id):
    try:
        #se intenta obtener las citas medicas específicas según el ID proporcionado.
        cita = CitaMedica.objects.get(pk=cita_id)

        if request.method == 'POST':
            #se verifica si se ha enviado un campo desde el formulario del template de confirmación(name="confirmar_cita")
            if 'confirmar_cita' in request.POST:
                #se marca la cita como confirmada y crea un evento en el calendario.
                cita.confirmado = True
                cita.save()

                #se crea un nuevo evento en el calendario
                #instancia de la clase Event
                event = Event()

                #se asocia el evento a calendario llamado 'Calendar' y se asigna la propiedad alendar del evento
                event.calendar = Calendar.objects.get(name='Calendar')
                
                #se establecen los atributos del evento event
                event.title = cita.motivo
                event.start = cita.fecha
                event.end = cita.fecha
                
                #se guarda el evento en la base de datos
                event.save()
                
                #se redirige a la vista de citas confirmadas
                return redirect('citas_app:vista_solicitudes_medico')

        #se obtienen los eventos de las citas confirmadas
        eventos = obtener_eventos(request)
        
        #se renderiza la plantilla HTML con los datos de la cita y los eventos
        return render(request, 'doctors/confirmacion_citas.html', {'cita': cita, 'eventos': eventos})

    except CitaMedica.DoesNotExist:
        #se maneja la excepcion si la cita no existe y redirige a la vista de citas solicitadas por el medico
        return redirect('citas_app:vista_solicitudes_medico')


#vista encargada de mostrar el calendario de citas medicas confirmadas para el medico en sesion
@method_decorator(login_required, name='dispatch')
class CitasConfirmadasCalendar(TemplateView):
    
    #se define la plantilla HTML a utilizar
    template_name = 'doctors/calendario_citas_confirmadas.html'

    #se obtiene el contexto de la superclase.
    def get_context_data(self, request, **kwargs):
        context = super().get_context_data(**kwargs)

        #se obtiene los eventos de las citas confirmadas
        eventos = obtener_eventos(request)

        #se marca la URL del calendario como segura.
        context['calendar'] = mark_safe(reverse('citas_app:citas_confirmadas_calendar'))

        #se pasan los eventos al contexto.
        context['eventos'] = eventos

        #se devuelve el contexto ya modificado
        return context


#vista para completar la cita del paciente
@permiso_medico
def completar_cita(request, cita_id):
    #se obtiene el médico actualmente autenticado
    medico = request.user.medico

    #se recuperan las solicitudes de citas relacionadas con este médico
    solicitudes_citas = CitaMedica.objects.filter(medico=medico, pk=cita_id)
    
    #se obtiene la cita médica específica
    cita = get_object_or_404(CitaMedica, pk=cita_id)

    #se verifica que el medico en la sesion actual este relacionado con esta cita
    if cita.medico != request.user.medico:
        return redirect('citas_app:vista_solicitudes_medico')

    #se verifica que la cita aun no se haya completado
    if cita.completada:
        return redirect('citas_app:vista_solicitudes_medico')

    #se carga el formulario CompletarHistorialForm
    if request.method == 'POST':
        form = CompletarHistorialForm(request.POST)

        #se valida
        if form.is_valid():
            # se crea un objeto CompletarHistorial
            completar_historial = form.save(commit=False)
            completar_historial.cita_medica = cita
            completar_historial.paciente = cita.paciente
            completar_historial.save()

            #se marca la cita como completada
            cita.completada = True
            cita.save()
            
            #messages.success(request, f'Tu cita con el doctor {cita.medico.nombre_medico} {cita.medico.apellido_medico}, ha finalizado {cita.fecha} puedes revisar detalles en tu historial medico')
            
            #se redirige a la vista en caso de ser guardada correctamente
            return redirect('citas_app:vista_solicitudes_medico')
    
    #caso contrario se renderiza el formualio vacio
    else:
        form = CompletarHistorialForm()

    #se redneriza el template pasandole el contexto
    return render(request, 'doctors/completar_info_cita.html', {'form': form, 'cita': cita, 'solicitudes_citas':solicitudes_citas})


#vista para mostrar el historial medico del paciente desde el perfil del medico
def ver_historial(request, cita_id):
    try:
        #se obtiene el medico en sesion
        medico = request.user.medico
        
        #se obtiene las solicitudes del medico
        solicitudes_citas = CitaMedica.objects.filter(medico=medico)
        
        #se obtienen las citas medicas
        cita = CitaMedica.objects.get(pk=cita_id)
        
        #se obtiene el historial total
        historial = CompletarHistorial.objects.filter(cita_medica=cita).first()
        
        #se renderiza el template pasando el diccionario
        return render(request, 'doctors/ver_historial.html', {'cita':cita, 'historial': historial,'solicitudes_citas': solicitudes_citas,})
    
    #caso contrario arroja un error y devuelve la vista citas_app:vista_solicitudes_medico
    except CitaMedica.DoesNotExist:
        return redirect('citas_app:vista_solicitudes_medico')
    
    
#vista para mostrar el historial medico del paciente desde el perfil del paciente
def ver_historial_personal(request, cita_id):
    try:
        paciente = request.user.paciente
        
        solicitudes_citas = CitaMedica.objects.filter(paciente=paciente)
        
        #se obtienen las citas medicas
        ficha_cita = CitaMedica.objects.get(pk=cita_id)
        
        #se obtiene el historial total
        ficha_historial = CompletarHistorial.objects.filter(cita_medica=ficha_cita).first()
        
        #se renderiza el template pasando el diccionario
        return render(request, 'CRUD_appointments/ver_historial_personal.html', {'ficha_cita':ficha_cita, 'ficha_historial': ficha_historial,'solicitudes_citas': solicitudes_citas,})
        
    #caso contrario arroja un error y devuelve la vista citas_app:vista_solicitudes_medico
    except CitaMedica.DoesNotExist:
        return redirect('citas_app:appointments_list')
        

#vista para ver el historial completo de los pacientes desde el perfil del medico
@permiso_medico
def ver_historial_completo(request, paciente_id):
    #se recuperan todos los pacientes
    pacientes = Paciente.objects.all()

    #se recupera el paciente por su id
    paciente = get_object_or_404(Paciente, pk=paciente_id)

    #se recuperan todos los historiales médicos asociados a este paciente
    historiales = CompletarHistorial.objects.filter(paciente=paciente)

    #se renderiza rl template pasando el diccionario
    return render(request, 'doctors/ver_historial_completo.html', {'paciente': paciente, 'historiales': historiales,'pacientes':pacientes})


#vista encargada de la reprogramacion de citas
@permiso_medico
def reprogramar_cita(request, cita_id):
    #se obtienen las citas medicas por su id
    cita = CitaMedica.objects.get(pk=cita_id)
    
    #se obtienen los eventos para mostrar en el calendario
    eventos = obtener_eventos(request)

    #se valida y se almacenda el formulario
    if request.method == 'POST':
        form = ReprogramarCitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            #messages.success(request, f'Tienes una cita reprogramada con el médico {cita.medico.nombre_medico} {cita.medico.apellido_medico}. revisa lista de citas para mas detalles')
            
            #se redirige al template del paciente
            return redirect('citas_app:vista_solicitudes_medico')
    
    #caso contrario se renderiza el mismo formulario
    else:
        form = ReprogramarCitaForm(instance=cita)
    
    #se pasan los datos por contexto   
    context = {
        'form': form,
        'cita':cita,
        'eventos':eventos,
        }

    #se renderiza el template encargado de mostrar la informacion
    return render(request, 'doctors/reprogramar_cita.html', context )


#metodo para obtener los dias disponibles
def obtener_dias_disponibles():
    #se obtiene la fecha actual
    fecha_actual = datetime.now().date()
    
    #se obtiene la fecha limite con los dias a mostr a partir de la fecha actual
    fecha_limite = fecha_actual + timedelta(days=20)

    #se obtienen las fechas de la citas confirmadas filtrandose por mes y año
    fechas_confirmadas = CitaMedica.objects.filter(
        fecha__month=fecha_actual.month,
        fecha__year=fecha_actual.year,
        confirmado=True
    ).values_list('fecha', flat=True)

    #se genera una lista de fechas para los proximos 20 días, excluyendo los domingos, las fechas pasadas y las fechas confirmadas
    dias_disponibles = [
        fecha for fecha in [fecha_actual + timedelta(days=i) for i in range(20)]
        if fecha.weekday() != 6    #se excluye los domingos
        and fecha <= fecha_limite  #se excluyen las fechas pasadas
        and fecha not in fechas_confirmadas  #se excluyen las fechas confirmadas
    ]
    #se devuelven los dias resultantes disponibles
    return dias_disponibles


#vista encargada de mostrar el historial de citas al paciente
def historial_completo_paciente(request):
    #se recupera el historial del paciente actual
    paciente = request.user.paciente

    #se filtra las citas médicas finalizadas
    citas_finalizadas = CitaMedica.objects.filter(paciente=paciente, completada=True)

    #se obtiene el historial relacionado con las citas finalizadas
    historial = CompletarHistorial.objects.filter(cita_medica__in=citas_finalizadas)

    #se obtienen las citas solicitadas por el paciente
    cita = CitaMedica.objects.filter(paciente=paciente)

    return render(request, 'patients/historial_completo_paciente.html', {'historial': historial, 'cita': cita})


#vista encargada de mostrar las especialidades disponibles
@login_required
def EspecialidadesView(request):
    #se obtienen todos los medicos
    medicos = Medico.objects.all()
    
    #se pasan al contexto
    context = {
        'medicos': medicos,
    }

    #se renderiza el template
    return render(request, 'doctors/especialidades.html', context)


#vista encargada de mostrar todas la citas totales almacenadas en el sistema
@permiso_medico
def citas_generales(request):
    #se obtienen todas las citas
    citas = CitaMedica.objects.all()
    
    #se obtiene el numero de citas almacenadas
    total_citas = CitaMedica.objects.count()
    
    #se obtiene el numer de pacientes 
    pacientes = Paciente.objects.count()
    
    #se obtiene el numer de medicos 
    medicos = Medico.objects.count()
    
    #se pasa todo al contexto
    context = {
        'citas': citas,
        'total_citas':total_citas,
        'pacientes':pacientes,
        'medicos':medicos,
    }
    
    #se renderiza el template que mostrara toda la informacion
    return render(request, 'doctors/citas_generales.html', context)
