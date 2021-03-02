from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, TemplateView, View
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


from .tokens import account_activation_token
from .forms import RegisterUserForm
from .models import Profile


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Profile
    fields = ['first_name', 'last_name', 'email_confirmed']
    success_message = "%(first_name)s your information was updated successfully"

    def test_func(self):
        return self.request.user == self.request.user.profile.user

    def get_success_url(self):
        return reverse('accounts:profile', kwargs={'pk': self.request.user.pk})


class LoginView(UserPassesTestMixin, LoginView):
    template_name = 'auth/login.html'

    def handle_no_permission(self):
        messages.warning(self.request, 'You are already logged in!')
        return redirect(self.request.user.profile.get_absolute_url())

    def test_func(self):
        return self.request.user.is_anonymous   

    def get_success_url(self):
        messages.warning(self.request, 'logged in!')
        return reverse('accounts:profile', kwargs={'pk': self.request.user.pk})


class LogOutView(LogoutView):
    template_name = 'auth/logout.html'

    def logged_in_message(self):
        return messages.warning(self.request, 'You have been logged out')


class RegisterUserView(UserPassesTestMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'accounts/register.html'
    success_url = 'accounts:activation_email_sent'

    def handle_no_permission(self):
        messages.warning(self.request, 'You are already registered!')
        return redirect(self.request.user.profile.get_absolute_url())
        # return redirect('installs:installation-list')

    def test_func(self):
        return self.request.user.is_anonymous

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        current_site = Site.objects.get_current()
        subject = 'Activate your account'
        message = render_to_string('accounts/account_activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        user.email_user(subject, message)
        return redirect('accounts:activation_email_sent')
        return super().form_valid(form)


class ActivationEmailSentView(TemplateView):
    template_name = 'accounts/activation_email_sent.html'


class ActivateView(View):

    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.profile.email_confirmed = True
            user.save()
            return redirect('/')
