from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.http import HttpResponse
from django.views.generic import FormView
from django.shortcuts import render,redirect

class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'login.html'
    success_url = '/'

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
    return redirect('http://50.19.129.198:8080/login')
