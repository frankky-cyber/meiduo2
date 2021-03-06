from django.shortcuts import render
from rest_framework.views import APIView
from areas.models import Area
from rest_framework.response import Response
from areas.serializers import AreaSerializer, SubsSerializer
from rest_framework import status
from rest_framework.generics import ListAPIView,RetrieveAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet
# Create your views here.

# class  AreaListView(APIView):
#     """查询所有省  """
#     # 没用到分页
#     def get(self, request):
#         #获取指定的查询集
#         qs = Area.objects.filter(parent = None)
#         #创建序列化器进行序列化
#         serializer = AreaSerializer(instance=qs, many = True)
#         #响应
#         return Response(serializer.data)


# class AreaDetailView(APIView):
#     """查询单一省或市"""
#     def get(self, request, pk):
#         # 根据pk查询出省或者市对象
#         try:
#             area = Area.objects.get(id = pk)
#         except Area.DoesNotExist:
#             return Response({'message':'无效pk'}, status=status.HTTP_400_BAD_REQUEST)
#         # 创建序列化器对象进行序列化
#         serializer = SubsSerializer(instance=area,many = False)
#         # 响应
#         return Response(serializer.data)


# class  AreaListView(ListAPIView):
#     serializer_class = AreaSerializer
#     queryset = Area.objects.filter(parent = None)


# class AreaDetailView(RetrieveAPIView):
#     serializer_class = SubsSerializer
#     queryset =  Area.objects.all()


class AreaViewSet(ReadOnlyModelViewSet):
    def get_queryset(self):
        """重写次方法"""
        if self.action =='list':
            return Area.objects.filter(parent = None)
        else:
            return Area.objects.all()
        
    def get_serializer_class(self):
        if self.action =='list':
            return AreaSerializer
        else:
            return SubsSerializer