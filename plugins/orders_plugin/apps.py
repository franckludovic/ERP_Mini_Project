from django.apps import AppConfig


class OrdersPluginConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "plugins.orders_plugin"
    label = "orders_plugin"
    verbose_name = "Orders"

    def ready(self):
        pass