from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from main.views import FullNetworkViewset, PartNetworkViewset, get_network_obj_high_avg


router = DefaultRouter()
router.register("full-network", FullNetworkViewset, basename='full-network') # Получение списка торговых сетей
router.register("part-network", PartNetworkViewset, basename='part-network') # Получение звеньев торговых сетей


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dept-high-avg/', get_network_obj_high_avg, name='dept-high-avg'),
    path('', include(router.urls)),

]