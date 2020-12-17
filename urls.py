from django.urls import path
from . import views


urlpatterns = [
    path('api/', views.get_data_from_db),
    # path('api/thread1/', views.get_sla_policy1),
    path('api/threading/', views.threading_task),
    path('api/result/', views.show_result),
    path('api/insert/', views.insert_data),
    path('api/update/', views.update_data),
    path('api/reset/', views.database_reset),
    path('api/timer/', views.timer),
    path('api/checktime/', views.check_created_time),
]

