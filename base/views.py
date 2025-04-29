from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout


from . import models


# Create your views here.


class TaskList(LoginRequiredMixin, ListView):
    model = models.Task
    context_object_name = "tasks"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = context["tasks"].filter(user=self.request.user)
        context["count"] = context["tasks"].filter(complete=False).count()

        search_input = self.request.GET.get("search-area") or ""
        if search_input:
            context["tasks"] = context["tasks"].filter(title__icontains=search_input)

        context["search_input"] = search_input

        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = models.Task
    context_object_name = "task"
    template_name = "base/task.html"


class TaskCreate(LoginRequiredMixin, CreateView):
    model = models.Task
    fields = ["title", "description", "complete"]
    success_url = reverse_lazy("tasks")
    template_name = "base/task_form.html"


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = models.Task
    fields = ["title", "description", "complete"]
    success_url = reverse_lazy("tasks")
    template_name = "base/task_form.html"


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = models.Task
    context_object_name = "task"
    success_url = reverse_lazy("tasks")
    template_name = "base/task_confirm_delete.html"


class CustomLoginView(LoginView):
    template_name = "base/login.html"
    fields = "__all__"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("tasks")


class CustomLogoutView(LogoutView):
    next_page = "login"

    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return redirect(self.next_page)


class RegisterPage(FormView):
    template_name = "base/register.html"
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy("tasks")

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("tasks")
        return super().get(request, *args, **kwargs)
