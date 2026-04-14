from django.apps import AppConfig


class CustomerPluginConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "plugins.customer_plugin"
    label = "customer_plugin"
    verbose_name = "Customer"

    def ready(self):
        pass