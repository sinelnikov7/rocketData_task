from django.shortcuts import render
from rest_framework.response import Response

from .models import NetworkNode
from .serializer import NetworkSerializer

from rest_framework import viewsets

class NetworkViewset(viewsets.ModelViewSet):
    """Получение всех торговых сетей"""
    queryset = NetworkNode.objects.filter(network_endpoint=True)
    serializer_class = NetworkSerializer

    # def list(self, request, *args, **kwargs):
    #     queryset = NetworkNode.objects.all()
    #     for i in queryset:
    #         print(i)
    #     return Response({"qqq":222})
# Create your views here.
