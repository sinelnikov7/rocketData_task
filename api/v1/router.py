from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from main.views import FullNetworkViewset, PartNetworkViewset, get_network_obj_high_avg, ProductViewset, get_qr_contacts


router = DefaultRouter()
router.register("full-network", FullNetworkViewset, basename='full-network') # Торговые сети
router.register("part-network", PartNetworkViewset, basename='part-network') # Объекты торговых сетей
router.register("product", ProductViewset, basename='product') # Продукты торговых сетей

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dept-high-avg/', get_network_obj_high_avg, name='dept-high-avg'), # Получить объекты с задолженностью выше среднего
    path('get-qr-contacts/<int:pk>', get_qr_contacts, name='get-qr-contacts'), # Получить QR код с контактами объекта
    path('', include(router.urls)),

]