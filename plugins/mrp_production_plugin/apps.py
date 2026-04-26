from django.apps import AppConfig


class MRPProductionPluginConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "plugins.mrp_production_plugin"
    label = "mrp_production_plugin"
    verbose_name = "MRP Production"

    def ready(self):
        pass
