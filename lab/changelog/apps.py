from django.apps import AppConfig


class ChangelogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'changelog'  # Replace with your actual app name

    def ready(self):
        """
        This method is called when Django is ready.
        We can use this to ensure our dynamic models are created.
        """
        # Import all models that use ChangeLogMixin to trigger setup
        from django.apps import apps

        # Get all models that use ChangeLogMixin
        for model in apps.get_models():
            if hasattr(model, '_ensure_changelog_setup'):
                model._ensure_changelog_setup()
