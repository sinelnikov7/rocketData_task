from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg

from .models import NetworkNode
from .permisions import IsActivate
from .serializer import FulNetworkSerializer, PartNetworkSerializer
from .filters import NetworkFilter


class FullNetworkViewset(mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """Представление списка торговых сетей"""
    queryset = NetworkNode.objects.all()
    serializer_class = FulNetworkSerializer
    permission_classes = (IsActivate,)

    def list(self, request, *args, **kwargs):
        """Получение списка всех торговых сетей"""
        queryset = NetworkNode.objects.filter(network_endpoint=True)
        response = self.serializer_class(queryset, many=True)
        return Response(response.data, status=status.HTTP_200_OK)


class PartNetworkViewset(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """Получение списка всех торговых сетей"""
    queryset = NetworkNode.objects.all()
    serializer_class = PartNetworkSerializer
    permission_classes = (IsActivate,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = NetworkFilter

    def list(self, request, *args, **kwargs):
        """Представление списка всех звеньев торговых сетей"""
        queryset = self.filter_queryset(NetworkNode.objects.all())
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
        obj_id = kwargs.get('pk')
        serializer = PartNetworkSerializer(data=request.data)
        try:
            instanse = NetworkNode.objects.get(id=obj_id)
            if serializer.is_valid():
                response = serializer.update(instanse, serializer.validated_data)
                return Response(PartNetworkSerializer(response).data, status=status.HTTP_200_OK)
            else:
                return Response({"errors": serializer.errors})

        except ObjectDoesNotExist:
            return Response({'error': f'Записи с id = {obj_id} не найдено'})

    def destroy(self, request, *args, **kwargs):
        obj_id = kwargs.get('pk')
        try:
            instanse = NetworkNode.objects.get(id=obj_id)
            instanse.delete()
        except ObjectDoesNotExist:
            return Response({'error': f'Записи с id = {obj_id} не найдено'})
        return Response({'success': True}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsActivate])
def get_network_obj_high_avg(request):
    """Получение объектов сети с задолженностью выше среднего"""
    queryset = NetworkNode.objects.filter(debt__gt=float(NetworkNode.objects.filter(debt__gt=0).aggregate(debt_avg=Avg('debt')).get('debt_avg')))
    response = PartNetworkSerializer(queryset, many=True)
    return Response(response.data, status=status.HTTP_200_OK)

