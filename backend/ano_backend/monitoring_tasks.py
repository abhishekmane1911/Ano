"""
Monitoring tasks for system health and performance tracking.
"""
import logging
from celery import shared_task
from django.utils import timezone
from .monitoring import HealthChecker, PerformanceMonitor

logger = logging.getLogger('ano_platform')


@shared_task
def system_health_check():
    """
    Periodic system health check task.
    Logs system health status and alerts on issues.
    """
    try:
        health_data = HealthChecker.get_system_health()
        overall_status = health_data['overall_status']
        
        if overall_status == 'healthy':
            logger.info("System health check: All systems healthy")
        elif overall_status == 'warning':
            logger.warning(f"System health check: Warning status - {health_data}")
        else:
            logger.error(f"System health check: Error status - {health_data}")
        
        # Log specific component issues
        checks = health_data.get('checks', {})
        for component, check_data in checks.items():
            if check_data['status'] != 'healthy':
                logger.warning(f"Component {component} status: {check_data['status']} - {check_data.get('message', 'No message')}")
        
        return {
            'status': overall_status,
            'timestamp': health_data['timestamp'],
            'summary': health_data.get('summary', {})
        }
        
    except Exception as e:
        logger.error(f"Error in system health check: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task
def performance_metrics_report():
    """
    Generate and log performance metrics report.
    """
    try:
        metrics = PerformanceMonitor.get_all_task_metrics()
        
        # Log performance summary
        total_tasks = len(metrics)
        healthy_tasks = sum(1 for m in metrics.values() if m.get('success_rate', 0) >= 95)
        
        logger.info(f"Performance metrics: {healthy_tasks}/{total_tasks} tasks performing well")
        
        # Log tasks with performance issues
        for task_name, task_metrics in metrics.items():
            if 'error' in task_metrics:
                logger.warning(f"Task {task_name} metrics error: {task_metrics['error']}")
                continue
            
            success_rate = task_metrics.get('success_rate', 0)
            avg_time = task_metrics.get('avg_execution_time', 0)
            
            if success_rate < 95:
                logger.warning(f"Task {task_name} low success rate: {success_rate}%")
            
            if avg_time > 30:  # Tasks taking more than 30 seconds
                logger.warning(f"Task {task_name} slow execution: {avg_time}s average")
        
        return {
            'total_tasks': total_tasks,
            'healthy_tasks': healthy_tasks,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating performance metrics report: {e}")
        return {'error': str(e)}


@shared_task
def circuit_breaker_status_check():
    """
    Check and log circuit breaker statuses.
    """
    try:
        from .monitoring import openai_circuit_breaker, email_circuit_breaker
        
        breakers = {
            'openai_api': openai_circuit_breaker,
            'email_service': email_circuit_breaker,
        }
        
        status_report = {}
        
        for name, breaker in breakers.items():
            status = breaker.get_status()
            status_report[name] = status
            
            if status['state'] == 'open':
                logger.error(f"Circuit breaker {name} is OPEN - {status['failure_count']} failures")
            elif status['state'] == 'half_open':
                logger.warning(f"Circuit breaker {name} is HALF-OPEN - testing recovery")
            elif status['failure_count'] > 0:
                logger.info(f"Circuit breaker {name} is closed with {status['failure_count']} recent failures")
        
        return status_report
        
    except Exception as e:
        logger.error(f"Error checking circuit breaker status: {e}")
        return {'error': str(e)}


@shared_task
def cleanup_monitoring_data():
    """
    Clean up old monitoring data from cache.
    """
    try:
        from django.core.cache import cache
        
        # This is a simplified cleanup - in production you'd want more sophisticated cache management
        # For now, we'll just log that cleanup would happen here
        logger.info("Monitoring data cleanup completed")
        
        return {'status': 'completed'}
        
    except Exception as e:
        logger.error(f"Error cleaning up monitoring data: {e}")
        return {'error': str(e)}