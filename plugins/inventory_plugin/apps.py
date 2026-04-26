from django.apps import AppConfig


class InventoryPluginConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "plugins.inventory_plugin"
    label = "inventory_plugin"
    verbose_name = "Inventory"

    def ready(self):
        pass
