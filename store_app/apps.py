from django.apps import AppConfig


class StoreAppConfig(AppConfig):
    name = 'store_app'

    def ready(self):
        import store_app.signals
