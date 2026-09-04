from django.urls import path
from apps.notifications.views import (
    TriggerListCreateView,
    TriggerDetailView,
    TemplateListCreateView,
    TemplateDetailView,
    TemplateToggleView,
    TemplateTestView,
    DeliveryListView,
)

urlpatterns = [
    path("triggers/", TriggerListCreateView.as_view(), name="notification-triggers-list-create"),
    path("triggers/<int:pk>/", TriggerDetailView.as_view(), name="notification-triggers-detail"),
    path("templates/", TemplateListCreateView.as_view(), name="notification-templates-list-create"),
    path("templates/<int:pk>/", TemplateDetailView.as_view(), name="notification-templates-detail"),
    path("templates/<int:pk>/toggle/", TemplateToggleView.as_view(), name="notification-templates-toggle"),
    path("templates/<int:pk>/test/", TemplateTestView.as_view(), name="notification-templates-test"),
    path("deliveries/", DeliveryListView.as_view(), name="notification-deliveries-list"),
]
