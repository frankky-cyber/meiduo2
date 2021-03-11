from django.conf.urls import url
from areas.views import AreaViewSet
from rest_framework import routers
router  = routers.DefaultRouter()
urlpatterns = [
    # # 查询所有省
    # url(r"^areas/$", AreaListView.as_view({'get':'list'})),
    # url(r"^areas/(?P<pk>\d+)/$", AreaDetailView.as_view({'get':'retrieve'})), #不需要自己写了
    
]
router  = routers.DefaultRouter()
router.register(r"areas", AreaViewSet, base_name='area')  # 注意这里必须指定base_name　默认会找queryset里面的模型的名字的小写但是我们没有定义queryset如果这里不指定的话就会断言（输出一句话也不是报错）
urlpatterns += router.urls

