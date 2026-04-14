from django.apps import AppConfig


class AuthPluginConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "plugins.auth_plugin"
    label = "auth_plugin"
    verbose_name = "Authentication"

    def ready(self):
        pass