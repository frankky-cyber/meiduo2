from django.conf.urls import url
from users import views
from rest_framework_jwt.views import obtain_jwt_token
urlpatterns = [
    #注册用户
    url(r'^users/$', views.UserView.as_view()),
    # 判断用户名是否已注册
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    # 判断手机号是否已注册
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    # JWT登录　这个视图帮你完成校验　签发token最后响应　其实是封装了django自带的验证然后加了token再然后响应
    url(r'^authorizations/$', obtain_jwt_token),  
]