from django.apps import AppConfig


class PanelConfig(AppConfig):
    name = "apps.panel"
    label = "panel"
    verbose_name = "Yönetim paneli"

    def ready(self) -> None:
        from . import sinyaller  # noqa: F401
