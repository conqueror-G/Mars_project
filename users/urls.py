from django.urls import path
from users.views import SignupView,SigninView, AlertView,index


urlpatterns = [
    path('/signup',SignupView.as_view()),
    path('/signin',SigninView.as_view()),
    path('/alert',AlertView.as_view(http_method_names=['get'])),
    path('/alert/delete',AlertView.as_view(http_method_names=['delete'])),
    path('',index)
]