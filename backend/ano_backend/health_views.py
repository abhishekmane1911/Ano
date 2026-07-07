"""
Health check API endpoints for monitoring system status.
Provides REST API access to health check information.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .monitoring import HealthChecker, PerformanceMonitor, CircuitBreaker
from .monitoring import openai_circuit_breaker, email_circuit_breaker


@api_view(['GET'])
def health_check_basic(request):
    """Basic health check endpoint (no authentication required)"""
    try:
        # Basic checks that don't require admin privileges
        redis_check = HealthChecker.check_redis_connection()
        db_check = HealthChecker.check_database_connection()
        
        # Determine basic health status
        if redis_check['status'] == 'healthy' and db_check['status'] == 'healthy':
            overall_status = 'healthy'
            http_status = status.HTTP_200_OK
        else:
            overall_status = 'unhealthy'
            http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        
        return Response({
            'status': overall_status,
            'timestamp': HealthChecker.get_system_health()['timestamp'],
            'checks': {
                'redis': redis_check['status'],
                'database': db_check['status']
            }
        }, status=http_status)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Health check failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def health_check_detailed(request):
    """Detailed health check endpoint (admin only)"""
    try:
        health_data = HealthChecker.get_system_health()
        
        # Determine HTTP status based on overall health
        if health_data['overall_status'] == 'healthy':
            http_status = status.HTTP_200_OK
        elif health_data['overall_status'] == 'warning':
            http_status = status.HTTP_200_OK  # Still operational
        else:
            http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        
        return Response(health_data, status=http_status)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Detailed health check failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def performance_metrics(request):
    """Get performance metrics for async operations"""
    try:
        metrics = PerformanceMonitor.get_all_task_metrics()
        
        return Response({
            'timestamp': HealthChecker.get_system_health()['timestamp'],
            'metrics': metrics
        })
        
    except Exception as e:
        return Response({
            'error': f'Failed to get performance metrics: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def circuit_breaker_status(request):
    """Get status of all circuit breakers"""
    try:
        circuit_breakers = {
            'openai_api': openai_circuit_breaker.get_status(),
            'email_service': email_circuit_breaker.get_status(),
        }
        
        return Response({
            'timestamp': HealthChecker.get_system_health()['timestamp'],
            'circuit_breakers': circuit_breakers
        })
        
    except Exception as e:
        return Response({
            'error': f'Failed to get circuit breaker status: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def reset_circuit_breaker(request, breaker_name):
    """Reset a specific circuit breaker"""
    try:
        circuit_breakers = {
            'openai_api': openai_circuit_breaker,
            'email_service': email_circuit_breaker,
        }
        
        if breaker_name not in circuit_breakers:
            return Response({
                'error': f'Unknown circuit breaker: {breaker_name}',
                'available': list(circuit_breakers.keys())
            }, status=status.HTTP_400_BAD_REQUEST)
        
        breaker = circuit_breakers[breaker_name]
        
        # Reset the circuit breaker
        breaker._set_state("closed")
        breaker._reset_failure_count()
        
        return Response({
            'message': f'Circuit breaker {breaker_name} has been reset',
            'status': breaker.get_status()
        })
        
    except Exception as e:
        return Response({
            'error': f'Failed to reset circuit breaker: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def task_metrics(request, task_name=None):
    """Get metrics for a specific task or all tasks"""
    try:
        if task_name:
            # Get metrics for specific task
            metrics = PerformanceMonitor.get_task_metrics(task_name)
            if 'error' in metrics:
                return Response(metrics, status=status.HTTP_404_NOT_FOUND)
            return Response(metrics)
        else:
            # Get metrics for all tasks
            all_metrics = PerformanceMonitor.get_all_task_metrics()
            return Response({
                'timestamp': HealthChecker.get_system_health()['timestamp'],
                'tasks': all_metrics
            })
            
    except Exception as e:
        return Response({
            'error': f'Failed to get task metrics: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Simple health check for load balancers (no authentication, minimal response)
def health_ping(request):
    """Simple ping endpoint for load balancers"""
    try:
        # Just check if we can respond
        return JsonResponse({'status': 'ok'})
    except Exception:
        return JsonResponse({'status': 'error'}, status=503)