from django.apps import AppConfig


class ProductManagerPluginConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "plugins.product_manager_plugin"
    label = "product_manager_plugin"
    verbose_name = "Product Manager"

    def ready(self):
        pass
