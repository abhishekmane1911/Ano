from django.apps import AppConfig


class ModerationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "moderation"
    verbose_name = "AI Moderation System"
    
    def ready(self):
        """Import signals when the app is ready"""
        import moderation.signals
