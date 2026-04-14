from django.apps import AppConfig


class WarehousePluginConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "plugins.warehouse_plugin"
    label = "warehouse_plugin"
    verbose_name = "Warehouse"

    def ready(self):
        pass
