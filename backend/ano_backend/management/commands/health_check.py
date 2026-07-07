"""
Django management command for system health checks.
Provides comprehensive health monitoring for the advanced gamification modules.
"""
import json
from django.core.management.base import BaseCommand
from ano_backend.monitoring import HealthChecker, PerformanceMonitor


class Command(BaseCommand):
    help = 'Check system health for advanced gamification modules'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['json', 'text'],
            default='text',
            help='Output format (default: text)'
        )
        parser.add_argument(
            '--component',
            choices=['all', 'celery', 'redis', 'database', 'queues', 'performance'],
            default='all',
            help='Component to check (default: all)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information'
        )
    
    def handle(self, *args, **options):
        format_type = options['format']
        component = options['component']
        verbose = options['verbose']
        
        if component == 'all':
            health_data = HealthChecker.get_system_health()
            if verbose:
                health_data['performance'] = PerformanceMonitor.get_all_task_metrics()
        elif component == 'performance':
            health_data = PerformanceMonitor.get_all_task_metrics()
        else:
            # Check specific component
            health_data = self._check_specific_component(component)
        
        if format_type == 'json':
            self.stdout.write(json.dumps(health_data, indent=2))
        else:
            self._print_text_format(health_data, component, verbose)
    
    def _check_specific_component(self, component):
        """Check a specific system component"""
        if component == 'celery':
            return {'celery_workers': HealthChecker.check_celery_workers()}
        elif component == 'redis':
            return {'redis': HealthChecker.check_redis_connection()}
        elif component == 'database':
            return {'database': HealthChecker.check_database_connection()}
        elif component == 'queues':
            return {'task_queues': HealthChecker.check_task_queue_health()}
        else:
            return {'error': f'Unknown component: {component}'}
    
    def _print_text_format(self, health_data, component, verbose):
        """Print health data in text format"""
        if component == 'performance':
            self._print_performance_metrics(health_data)
            return
        
        if 'overall_status' in health_data:
            # Full system health check
            overall_status = health_data['overall_status']
            timestamp = health_data.get('timestamp', 'Unknown')
            
            # Print header
            status_color = self._get_status_color(overall_status)
            self.stdout.write(
                self.style.HTTP_INFO('=' * 60)
            )
            self.stdout.write(
                self.style.HTTP_INFO('SYSTEM HEALTH CHECK')
            )
            self.stdout.write(
                self.style.HTTP_INFO(f'Timestamp: {timestamp}')
            )
            self.stdout.write(
                status_color(f'Overall Status: {overall_status.upper()}')
            )
            self.stdout.write(
                self.style.HTTP_INFO('=' * 60)
            )
            
            # Print summary
            summary = health_data.get('summary', {})
            self.stdout.write(f"Components: {summary.get('total', 0)} total, "
                            f"{summary.get('healthy', 0)} healthy, "
                            f"{summary.get('warning', 0)} warning, "
                            f"{summary.get('error', 0)} error")
            self.stdout.write('')
            
            # Print individual checks
            checks = health_data.get('checks', {})
            for check_name, check_data in checks.items():
                self._print_check_result(check_name, check_data, verbose)
            
            # Print performance metrics if included
            if 'performance' in health_data:
                self.stdout.write(self.style.HTTP_INFO('\nPERFORMANCE METRICS'))
                self.stdout.write(self.style.HTTP_INFO('-' * 40))
                self._print_performance_metrics(health_data['performance'])
        
        else:
            # Single component check
            for check_name, check_data in health_data.items():
                self._print_check_result(check_name, check_data, verbose)
    
    def _print_check_result(self, check_name, check_data, verbose):
        """Print individual check result"""
        status = check_data.get('status', 'unknown')
        message = check_data.get('message', 'No message')
        
        status_color = self._get_status_color(status)
        
        self.stdout.write(f"{check_name.replace('_', ' ').title()}: {status_color(status.upper())}")
        self.stdout.write(f"  Message: {message}")
        
        if verbose:
            # Print additional details
            for key, value in check_data.items():
                if key not in ['status', 'message']:
                    self.stdout.write(f"  {key}: {value}")
        
        self.stdout.write('')
    
    def _print_performance_metrics(self, metrics_data):
        """Print performance metrics"""
        if not metrics_data:
            self.stdout.write("No performance metrics available")
            return
        
        for task_name, metrics in metrics_data.items():
            if 'error' in metrics:
                self.stdout.write(f"{task_name}: {self.style.ERROR('ERROR')} - {metrics['error']}")
                continue
            
            self.stdout.write(f"\n{task_name}:")
            self.stdout.write(f"  Executions: {metrics.get('total_executions', 0)}")
            self.stdout.write(f"  Success Rate: {metrics.get('success_rate', 0)}%")
            self.stdout.write(f"  Avg Time: {metrics.get('avg_execution_time', 0)}s")
            self.stdout.write(f"  Min/Max Time: {metrics.get('min_execution_time', 0)}s / {metrics.get('max_execution_time', 0)}s")
    
    def _get_status_color(self, status):
        """Get appropriate color styling for status"""
        if status == 'healthy':
            return self.style.SUCCESS
        elif status == 'warning':
            return self.style.WARNING
        elif status in ['error', 'unhealthy']:
            return self.style.ERROR
        else:
            return self.style.NOTICE