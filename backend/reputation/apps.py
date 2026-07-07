from django.apps import AppConfig


class ReputationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "reputation"
    verbose_name = "Reputation System"
    
    def ready(self):
        """Import signals when the app is ready"""
        import reputation.signals
