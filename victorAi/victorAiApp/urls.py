from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import *
from .serializers import CustomUserTokenObtainSerializer

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(serializer_class=CustomUserTokenObtainSerializer), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/register/', RegisterView.as_view(), name='sign_up'),
    # path('test/', test_view.as_view(), name='sign_up'),
]
