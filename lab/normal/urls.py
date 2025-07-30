
from django.contrib import admin
from django.urls import path
from .views import InterfaceCreateView, InterfaceDeleteView, InterfaceUpdateView, InterfaceListView

urlpatterns = [
    path("interfaces/", InterfaceListView.as_view()),
    path("interfaces/new", InterfaceCreateView.as_view()),
    path("interfaces/<int:pk>/", InterfaceUpdateView.as_view()),
    path("interfaces/<int:pk>/delete", InterfaceDeleteView.as_view())
]