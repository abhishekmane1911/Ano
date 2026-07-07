"""
Performance monitoring and health checks for advanced gamification modules.
Provides monitoring for async operations, circuit breakers for external APIs,
and health checks for background services.
"""
import time
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

logger = logging.getLogger('ano_platform')


class PerformanceMonitor:
    """Monitor performance of async operations and tasks"""
    
    @staticmethod
    def monitor_task_performance(task_name: str):
        """Decorator to monitor task execution time and success rate"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                success = False
                error = None
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    return result
                except Exception as e:
                    error = str(e)
                    raise
                finally:
                    execution_time = time.time() - start_time
                    PerformanceMonitor._record_task_metrics(
                        task_name, execution_time, success, error
                    )
            
            return wrapper
        return decorator
    
    @staticmethod
    def _record_task_metrics(task_name: str, execution_time: float, success: bool, error: Optional[str]):
        """Record task performance metrics"""
        try:
            # Store metrics in cache with TTL
            cache_key_prefix = f"task_metrics:{task_name}"
            
            # Update execution time statistics
            times_key = f"{cache_key_prefix}:times"
            times = cache.get(times_key, [])
            times.append(execution_time)
            
            # Keep only last 100 executions
            if len(times) > 100:
                times = times[-100:]
            
            cache.set(times_key, times, timeout=3600)  # 1 hour
            
            # Update success/failure counts
            success_key = f"{cache_key_prefix}:success"
            failure_key = f"{cache_key_prefix}:failure"
            
            if success:
                cache.set(success_key, cache.get(success_key, 0) + 1, timeout=3600)
            else:
                cache.set(failure_key, cache.get(failure_key, 0) + 1, timeout=3600)
                
                # Log slow or failed tasks
                if execution_time > 30 or not success:
                    logger.warning(f"Task {task_name} performance issue: "
                                 f"time={execution_time:.2f}s, success={success}, error={error}")
        
        except Exception as e:
            logger.error(f"Error recording task metrics for {task_name}: {e}")
    
    @staticmethod
    def get_task_metrics(task_name: str) -> Dict[str, Any]:
        """Get performance metrics for a task"""
        try:
            cache_key_prefix = f"task_metrics:{task_name}"
            
            times = cache.get(f"{cache_key_prefix}:times", [])
            success_count = cache.get(f"{cache_key_prefix}:success", 0)
            failure_count = cache.get(f"{cache_key_prefix}:failure", 0)
            
            total_executions = success_count + failure_count
            success_rate = (success_count / total_executions * 100) if total_executions > 0 else 0
            
            metrics = {
                'task_name': task_name,
                'total_executions': total_executions,
                'success_count': success_count,
                'failure_count': failure_count,
                'success_rate': round(success_rate, 2),
                'avg_execution_time': round(sum(times) / len(times), 2) if times else 0,
                'min_execution_time': round(min(times), 2) if times else 0,
                'max_execution_time': round(max(times), 2) if times else 0,
                'recent_executions': len(times)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting task metrics for {task_name}: {e}")
            return {'task_name': task_name, 'error': str(e)}
    
    @staticmethod
    def get_all_task_metrics() -> Dict[str, Dict[str, Any]]:
        """Get metrics for all monitored tasks"""
        # This would require scanning cache keys, which is not efficient
        # In production, you'd want to maintain a registry of monitored tasks
        monitored_tasks = [
            'reputation.tasks.calculate_user_reputation',
            'reputation.tasks.update_wilson_scores',
            'reputation.tasks.batch_tier_updates',
            'moderation.tasks.moderate_message_async',
            'moderation.tasks.update_user_heat_scores',
            'security.tasks.analyze_security_events',
            'security.tasks.migrate_user_emails_to_hash',
        ]
        
        all_metrics = {}
        for task_name in monitored_tasks:
            all_metrics[task_name] = PerformanceMonitor.get_task_metrics(task_name)
        
        return all_metrics


class CircuitBreaker:
    """Circuit breaker pattern for external API calls"""
    
    def __init__(self, name: str, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.cache_key_prefix = f"circuit_breaker:{name}"
    
    def _get_state(self) -> str:
        """Get current circuit breaker state"""
        return cache.get(f"{self.cache_key_prefix}:state", "closed")
    
    def _set_state(self, state: str):
        """Set circuit breaker state"""
        cache.set(f"{self.cache_key_prefix}:state", state, timeout=self.recovery_timeout * 2)
    
    def _get_failure_count(self) -> int:
        """Get current failure count"""
        return cache.get(f"{self.cache_key_prefix}:failures", 0)
    
    def _increment_failure_count(self):
        """Increment failure count"""
        current = self._get_failure_count()
        cache.set(f"{self.cache_key_prefix}:failures", current + 1, timeout=self.recovery_timeout * 2)
    
    def _reset_failure_count(self):
        """Reset failure count"""
        cache.delete(f"{self.cache_key_prefix}:failures")
    
    def _get_last_failure_time(self) -> Optional[float]:
        """Get timestamp of last failure"""
        return cache.get(f"{self.cache_key_prefix}:last_failure")
    
    def _set_last_failure_time(self):
        """Set timestamp of last failure"""
        cache.set(f"{self.cache_key_prefix}:last_failure", time.time(), timeout=self.recovery_timeout * 2)
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        state = self._get_state()
        
        # If circuit is open, check if we should try again
        if state == "open":
            last_failure = self._get_last_failure_time()
            if last_failure and (time.time() - last_failure) > self.recovery_timeout:
                self._set_state("half_open")
                logger.info(f"Circuit breaker {self.name} transitioning to half-open")
            else:
                raise CircuitBreakerOpenException(f"Circuit breaker {self.name} is open")
        
        try:
            result = func(*args, **kwargs)
            
            # Success - reset failure count and close circuit if it was half-open
            if state == "half_open":
                self._set_state("closed")
                self._reset_failure_count()
                logger.info(f"Circuit breaker {self.name} closed after successful call")
            
            return result
            
        except Exception as e:
            self._increment_failure_count()
            self._set_last_failure_time()
            
            failure_count = self._get_failure_count()
            
            # Open circuit if failure threshold is reached
            if failure_count >= self.failure_threshold:
                self._set_state("open")
                logger.error(f"Circuit breaker {self.name} opened after {failure_count} failures")
            
            raise e
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            'name': self.name,
            'state': self._get_state(),
            'failure_count': self._get_failure_count(),
            'failure_threshold': self.failure_threshold,
            'recovery_timeout': self.recovery_timeout,
            'last_failure': self._get_last_failure_time()
        }


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class HealthChecker:
    """Health checks for background services"""
    
    @staticmethod
    def check_celery_workers() -> Dict[str, Any]:
        """Check if Celery workers are running"""
        try:
            from celery import current_app
            
            # Get active workers
            inspect = current_app.control.inspect()
            active_workers = inspect.active()
            
            if active_workers:
                worker_count = len(active_workers)
                worker_names = list(active_workers.keys())
                
                return {
                    'status': 'healthy',
                    'worker_count': worker_count,
                    'workers': worker_names,
                    'message': f'{worker_count} Celery workers active'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'worker_count': 0,
                    'workers': [],
                    'message': 'No Celery workers found'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error checking Celery workers: {str(e)}'
            }
    
    @staticmethod
    def check_redis_connection() -> Dict[str, Any]:
        """Check Redis connection for Celery broker and cache"""
        try:
            # Test cache connection
            cache.set('health_check', 'test', timeout=10)
            cache_result = cache.get('health_check')
            cache.delete('health_check')
            
            if cache_result == 'test':
                return {
                    'status': 'healthy',
                    'message': 'Redis connection successful'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': 'Redis cache test failed'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Redis connection error: {str(e)}'
            }
    
    @staticmethod
    def check_database_connection() -> Dict[str, Any]:
        """Check database connection"""
        try:
            from django.db import connection
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
            
            if result and result[0] == 1:
                return {
                    'status': 'healthy',
                    'message': 'Database connection successful'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': 'Database query failed'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Database connection error: {str(e)}'
            }
    
    @staticmethod
    def check_task_queue_health() -> Dict[str, Any]:
        """Check health of task queues"""
        try:
            from celery import current_app
            
            # Get queue lengths
            inspect = current_app.control.inspect()
            active_queues = inspect.active_queues()
            
            if active_queues:
                queue_info = {}
                total_tasks = 0
                
                for worker, queues in active_queues.items():
                    for queue in queues:
                        queue_name = queue['name']
                        if queue_name not in queue_info:
                            queue_info[queue_name] = 0
                        # Note: This doesn't give us queue length, just active queues
                        # For actual queue lengths, you'd need to query Redis directly
                
                return {
                    'status': 'healthy',
                    'message': 'Task queues accessible',
                    'active_queues': list(queue_info.keys()),
                    'workers_with_queues': len(active_queues)
                }
            else:
                return {
                    'status': 'warning',
                    'message': 'No active queues found',
                    'active_queues': [],
                    'workers_with_queues': 0
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error checking task queues: {str(e)}'
            }
    
    @staticmethod
    def get_system_health() -> Dict[str, Any]:
        """Get overall system health status"""
        checks = {
            'celery_workers': HealthChecker.check_celery_workers(),
            'redis': HealthChecker.check_redis_connection(),
            'database': HealthChecker.check_database_connection(),
            'task_queues': HealthChecker.check_task_queue_health(),
        }
        
        # Determine overall status
        statuses = [check['status'] for check in checks.values()]
        
        if all(status == 'healthy' for status in statuses):
            overall_status = 'healthy'
        elif any(status == 'error' for status in statuses):
            overall_status = 'error'
        else:
            overall_status = 'warning'
        
        return {
            'overall_status': overall_status,
            'timestamp': timezone.now().isoformat(),
            'checks': checks,
            'summary': {
                'healthy': sum(1 for s in statuses if s == 'healthy'),
                'warning': sum(1 for s in statuses if s == 'warning'),
                'error': sum(1 for s in statuses if s == 'error'),
                'total': len(statuses)
            }
        }


# Global circuit breakers for external services
openai_circuit_breaker = CircuitBreaker("openai_api", failure_threshold=3, recovery_timeout=300)  # 5 minutes
email_circuit_breaker = CircuitBreaker("email_service", failure_threshold=5, recovery_timeout=180)  # 3 minutes


def monitor_async_operation(operation_name: str):
    """Decorator to monitor async operations"""
    return PerformanceMonitor.monitor_task_performance(operation_name)


def with_circuit_breaker(circuit_breaker: CircuitBreaker):
    """Decorator to add circuit breaker protection to functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return circuit_breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator