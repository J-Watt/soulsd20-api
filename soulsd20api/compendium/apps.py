from django.apps import AppConfig


class CompendiumConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'compendium'

    def ready(self):
        from . import signals  # noqa: F401
