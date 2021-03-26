from django.shortcuts import render
from rest_framework.generics import ListAPIView
from goods.models import SKU
from goods.serializers import SKUSerializer
from rest_framework.filters import OrderingFilter
# Create your views here.

class SKUListView(ListAPIView):
    """商品列表数据查询"""
    # queryset = SKU.objects.filter()
    filter_backends = [OrderingFilter]  # 指定过滤后端为排序过滤
    ordering_fields = ['create_time', 'price', 'sales']  # 指定排序字段 (查多中查的是那个模型中的数据,里面就指定那个模型的字段)
    
    serializer_class = SKUSerializer
    def get_queryset(self):
        # request.query_param.get() 这样放在这里是不行的
        # self.request.query_params.get()  #  这样行不行？一会检验一下就可以了　我觉得是可以的
        category_id = self.kwargs.get('category_id')
        # queryset = SKU.objects.filter(is_launched=True, category=category_id)
        queryset = SKU.objects.filter(is_launched=True, category_id=category_id)  #前端传的是id值
        return queryset

