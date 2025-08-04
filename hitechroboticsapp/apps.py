from django.apps import AppConfig


class HitechroboticsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # type: ignore
    name = 'hitechroboticsapp'

    def ready(self):
        import hitechroboticsapp.translation
