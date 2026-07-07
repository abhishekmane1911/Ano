from django.apps import AppConfig


class SecurityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "security"
    verbose_name = "Security & Privacy System"
    
    def ready(self):
        """Import signals when the app is ready"""
        import security.signals
