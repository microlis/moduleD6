from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .forms import UserForm


class UserDetailView(LoginRequiredMixin, DetailView):
    template_name = 'accounts/user_detail.html'
    queryset = User.objects.all()


class UserEditView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/user_edit.html'
    form_class = UserForm
    success_url = '/'

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return User.objects.get(pk=id)
