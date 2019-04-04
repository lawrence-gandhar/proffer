from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout, name='logout'),
    path('get-detials/', views.get_password, name='get-detials'),
    path('get-more-detials/', views.get_more_details, name='get-more-detials'),
    path('import-csv/', views.import_csv, name='import-csv'),
    path('location-select/', views.permission_location_select, name='location-select'),
    path('reports/', views.reports, name='reports'),
    path('get-edit-form/', views.get_edit_form, name='get-edit-form'),
    path('edit-form/', views.edit_form, name='edit-form'),
]