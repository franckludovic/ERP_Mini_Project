from django.apps import AppConfig


class UsersPluginConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "plugins.users_plugin"
    label = "users_plugin"
    verbose_name = "Users"

    def ready(self):
        pass