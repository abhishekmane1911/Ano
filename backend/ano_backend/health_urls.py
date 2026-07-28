from django.urls import path
from . import health_views

urlpatterns = [
    path('ping/', health_views.health_ping, name='health_ping'),
    path('health/', health_views.health_check_basic, name='health_basic'),
    
    # admin only
    path('health/detailed/', health_views.health_check_detailed, name='health_detailed'),
    path('health/performance/', health_views.performance_metrics, name='performance_metrics'),
    path('health/circuit-breakers/', health_views.circuit_breaker_status, name='circuit_breaker_status'),
    path('health/circuit-breakers/<str:breaker_name>/reset/', health_views.reset_circuit_breaker, name='reset_circuit_breaker'),
    
    path('health/tasks/', health_views.task_metrics, name='all_task_metrics'),
    path('health/tasks/<str:task_name>/', health_views.task_metrics, name='task_metrics'),
]