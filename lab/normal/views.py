from django.shortcuts import render
from django.views.generic import CreateView, ListView, DeleteView, UpdateView

from .forms import InterfaceForm
from .models import Interface

class InterfaceListView(ListView):
    model = Interface
    template_name = 'normal/list.html'
    context_object_name = 'interfaces'


class InterfaceCreateView(CreateView):
    model = Interface
    form_class = InterfaceForm
    template_name = 'normal/form.html'
    success_url = '/interfaces/'


class InterfaceUpdateView(UpdateView):
    model = Interface
    form_class = InterfaceForm
    template_name = 'normal/form.html'
    success_url = '/interfaces/'


class InterfaceDeleteView(DeleteView):
    model = Interface
    success_url = '/interfaces/'
