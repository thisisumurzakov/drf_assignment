from django.urls import path

from .views import CourierPatchGetView, OrderAssignView, OrderCompleteView, CourierPostView, OrderPostView, CView

urlpatterns = [
    path('couriers/', CourierPostView.as_view()),
    path('couriers2/', CView.as_view()),
    path('couriers/<int:pk>/', CourierPatchGetView.as_view()),
    path('orders/', OrderPostView.as_view()),
    path('orders/assign/', OrderAssignView.as_view()),
    path('orders/complete/', OrderCompleteView.as_view()),
]