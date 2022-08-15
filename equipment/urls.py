from django.urls import path
from equipment.views import EquipmentdetailView,HomeView
from equipment.views import (
    EquipmentRegisteredView,
    AdminListView,
    MatchView,
    EquipmentListView
)

urlpatterns = [
    path('/<int:equipment_id>/delete',EquipmentdetailView.as_view(http_method_names=['delete'])),
    path('/<int:equipment_id>/post',EquipmentdetailView.as_view(http_method_names=['post'])),
    path('/<int:equipment_id>',EquipmentdetailView.as_view(http_method_names=['get'])),
    path('/<int:equipment_id>/edit',EquipmentdetailView.as_view(http_method_names=['patch'])),
    path('/registered',EquipmentRegisteredView.as_view()),
    path('/match',MatchView.as_view(http_method_names=['post'])),
    path('/match/list',MatchView.as_view(http_method_names=['get'])),
    path('/match/delete',MatchView.as_view(http_method_names=['delete'])),
    path('/admin/list',AdminListView.as_view()),
    path('/list',EquipmentListView.as_view()),
    path('/list/delete',EquipmentListView.as_view(http_method_names=['delete'])),
    path('',HomeView.as_view())
]

