from django.apps import AppConfig


class AdminPluginConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "plugins.admin_plugin"
    label = "admin_plugin"
    verbose_name = "Admin"

    def ready(self):
        pass
