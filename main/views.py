from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg
import qrcode

from .models import NetworkNode, Product, User
from .permisions import IsActivate
from .serializer import FulNetworkSerializer, PartNetworkSerializer, ProductSerializer, ProductUpdateSerializer, PartNetworkUpdateSerializer
from .filters import NetworkFilter
from .tasks import send_email
from .services import get_user_id


class FullNetworkViewset(mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """Представление списка торговых сетей"""
    queryset = NetworkNode.objects.all()
    serializer_class = FulNetworkSerializer
    permission_classes = (IsActivate,)

    def list(self, request, *args, **kwargs):
        """Получение списка всех торговых сетей"""
        queryset = NetworkNode.objects.filter(network_endpoint=True, author=get_user_id(request))
        response = self.serializer_class(queryset, many=True)
        return Response(response.data, status=status.HTTP_200_OK)


class PartNetworkViewset(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """Представление всех звеньев торговых сетей"""
    queryset = NetworkNode.objects.all()
    serializer_class = PartNetworkSerializer
    permission_classes = (IsActivate,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = NetworkFilter

    def list(self, request, *args, **kwargs):
        """Получение списка всех звеньев торговых сетей"""
        queryset = self.filter_queryset(NetworkNode.objects.filter(author=get_user_id(request)))
        response = self.serializer_class(queryset, many=True)
        return Response(response.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """Создание объекта торговой сети"""
        serializer = PartNetworkSerializer(data=request.data)
        if serializer.is_valid():
            new_obj = serializer.create(serializer.validated_data)
            return Response(PartNetworkSerializer(new_obj).data, status=status.HTTP_201_CREATED)
        else:
            return Response({"errors": serializer.errors})

    def partial_update(self, request, *args, **kwargs):
        """Обновление объектов торговой сети"""
        user_id = get_user_id(request)
        obj_id = kwargs.get('pk')
        data = request.data
        data.pop('debt', None)
        serializer = PartNetworkUpdateSerializer(data=data)
        try:
            instanse = NetworkNode.objects.get(id=obj_id)
            if instanse.author_id == user_id:
                if serializer.is_valid():
                    response = serializer.update(instanse, serializer.validated_data)
                    return Response(PartNetworkUpdateSerializer(response).data, status=status.HTTP_200_OK)
                else:
                    return Response({"errors": serializer.errors})
            else:
                return Response({'error': f'Вы не имеете доступа к записи с id = {obj_id}'}, status=status.HTTP_403_FORBIDDEN)

        except ObjectDoesNotExist:
            return Response({'error': f'Записи с id = {obj_id} не найдено'})

    def destroy(self, request, *args, **kwargs):
        """Удаление объектов торговой сети"""
        obj_id = kwargs.get('pk')
        user_id = get_user_id(request)
        try:
            instanse = NetworkNode.objects.get(id=obj_id)
            if instanse.author_id == user_id:
                instanse.delete()
            else:
                return Response({'error': f'Вы не имеете доступа к записи с id = {obj_id}'}, status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return Response({'error': f'Записи с id = {obj_id} не найдено'})
        return Response({'success': True}, status=status.HTTP_200_OK)


class ProductViewset(mixins.CreateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """Представленик товаров"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsActivate,)

    def create(self, request, *args, **kwargs):
        """Создание объекта товара"""
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            new_obj = serializer.create(serializer.validated_data)
            return Response(ProductSerializer(new_obj).data, status=status.HTTP_201_CREATED)
        else:
            return Response({"errors": serializer.errors})

    def partial_update(self, request, *args, **kwargs):
        """Обновление объекта товара"""
        obj_id = kwargs.get('pk')
        serializer = ProductUpdateSerializer(data=request.data)
        try:
            instanse = Product.objects.get(id=obj_id)
            if serializer.is_valid():
                response = serializer.update(instanse, serializer.validated_data)
                return Response(ProductUpdateSerializer(response).data, status=status.HTTP_200_OK)
            else:
                return Response({"errors": serializer.errors})
        except ObjectDoesNotExist:
            return Response({'error': f'Записи с id = {obj_id} не найдено'})

    def destroy(self, request, *args, **kwargs):
        """Удаление объекта товара"""
        obj_id = kwargs.get('pk')
        try:
            instanse = Product.objects.get(id=obj_id)
            instanse.delete()
        except ObjectDoesNotExist:
            return Response({'error': f'Записи с id = {obj_id} не найдено'})
        return Response({'success': True}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsActivate])
def get_network_obj_high_avg(request):
    """Получение объектов сети с задолженностью выше среднего"""
    queryset = NetworkNode.objects.filter(debt__gt=float(NetworkNode.objects.filter(debt__gt=0, author=get_user_id(request)).aggregate(debt_avg=Avg('debt')).get('debt_avg')))
    response = PartNetworkSerializer(queryset, many=True)
    send_email.delay()
    return Response(response.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsActivate])
def get_qr_contacts(request, pk):
    """Получение qr кода с контактами объекта"""
    user_id = get_user_id(request)
    email = User.objects.get(id=user_id).email
    try:
        obj = NetworkNode.objects.get(id=pk)
    except ObjectDoesNotExist:
        return Response({'error': f'Записи с id = {pk} не найдено'}, status=status.HTTP_404_NOT_FOUND)
    response = f'Email - {obj.email}, адресс - {obj.country}, г.{obj.city} ул.{obj.street} - {obj.house_number}'
    img = qrcode.make(response)
    img_path = f"main/qr/qr-{obj.name}.png"
    img.save(img_path)
    send_email.delay(img_path=img_path, email=email)
    return Response({"status": "Письмо с qr кодом отправлено на почту"}, status=status.HTTP_200_OK)

