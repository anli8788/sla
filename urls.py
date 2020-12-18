from django.urls import path
from . import views


urlpatterns = [
    path('api/', views.get_data_from_db),
    # path('api/thread1/', views.get_sla_policy1),
    path('api/threading/', views.threading_task),
    path('api/result/', views.show_result),
    path('api/resultbyID/', views.get_data_byID),
    path('api/insert/', views.insert_data),
    path('api/update/', views.update_data),
    path('api/update1/', views.update_all_data),
    path('api/updateresult/', views.update_result),
    path('api/timer/', views.timer),
    path('api/checktime/', views.check_created_time),
    path('api/deleteone/', views.delete_one),
    path('api/deleteall/', views.delete_all),
]

