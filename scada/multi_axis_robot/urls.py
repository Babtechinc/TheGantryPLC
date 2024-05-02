from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('multi-axis-robot-control-mode/', views.control_mode, name="multi-axis-robot-control-mode"),
    path('multi-axis-robot-data-table/', views.data_table, name="multi-axis-robot-data-table"),
    path('receive-write-to-plc/', views.receive_write_to_plc, name="multi-axis-robot-receive-write-to-plc"),
    path('receive-stepper-data/', views.receive_stepper_data, name="multi-axis-robot-receive-data"),
    path('multi-axis-robot-graph/', views.graph, name="multi-axis-robot-graph"),

]