from django.apps import AppConfig


class NotificationsPluginConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "plugins.notifications_plugin"
    label = "notifications_plugin"
    verbose_name = "Notifications"

    def ready(self):
        pass
