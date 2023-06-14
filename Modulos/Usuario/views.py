from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.http import HttpResponse
from django.views.generic import FormView
from django.shortcuts import render,redirect
from django.conf import settings
from django.core.mail import send_mail
URL_SERVER = settings.URL_SERVER

class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'login.html'
    #success_url = '/'

    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated and user.groups.filter(name__in=['Administrador','Auditor']).exists():
            return '/'
        elif user.is_authenticated and user.groups.filter(name__in=['Comun']).exists():
            return '/egreso/'
        else:
            return '/'

    def form_valid(self, form):
        # Si el formulario es válido, inicia sesión al usuario y redirige a la página de éxito.
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)
    def form_invalid(self, form):
        # Manejar los errores si el formulario no es válido
        return render(self.request, self.template_name, {'form': form})


def logout(request):
    if 'username' in request.session:
        del request.session['username']
    return redirect(f'{URL_SERVER}login')


def send_correoe(request):
        # Enviar notificación por correo electrónico
        subject = 'Notificación'
        from_email = 'crecentosuperadm@gmail.com'
        recipient_list = ['eamezquita97@gmail.com']
        correo = send_mail(subject, 'Hola el mensaje a llegado!', from_email, recipient_list)
        return HttpResponse("return this string")