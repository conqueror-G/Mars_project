from django.urls import path

from devices.views   import DeviceDetailHistoryView, CategoryView, DeviceDetailView, DeviceDetailBatteryView, DeviceListView, DeviceDetailSetUpView
from equipment.views import DeviceRegisteredView
urlpatterns = [
    path('/registered', DeviceRegisteredView.as_view()),
    path('/category', CategoryView.as_view()),
    path('/detail/<int:equipment_gps_tracker_id>', DeviceDetailView.as_view()),
    path('/repair/<int:pk>/delete', DeviceDetailHistoryView.as_view(http_method_names=['delete'])),
    path('/repair/<int:equipment_gps_tracker_id>/post', DeviceDetailHistoryView.as_view(http_method_names=['post'])),
    path('/repair/<int:equipment_gps_tracker_id>', DeviceDetailHistoryView.as_view(http_method_names=['get'])),
    path('/battery/list/<int:equipment_gps_tracker_id>', DeviceDetailBatteryView.as_view(http_method_names=['get'])),
    path('/battery/<int:equipment_gps_tracker_id>', DeviceDetailBatteryView.as_view(http_method_names=['post'])),
    path('/battery/delete/<int:pk>', DeviceDetailBatteryView.as_view()),
    path('/list', DeviceListView.as_view()),
    path('/list/delete', DeviceListView.as_view(http_method_names=['delete'])),
    path('/setup/history/<int:equipment_gps_tracker_id>', DeviceDetailSetUpView.as_view())
    ]