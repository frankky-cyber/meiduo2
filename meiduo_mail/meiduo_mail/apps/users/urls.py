from django.conf.urls import url
from users import views
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework import routers
urlpatterns = [
    #注册用户
    url(r'^users/$', views.UserView.as_view()),
    # 判断用户名是否已注册
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    # 判断手机号是否已注册
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    # JWT登录　这个视图帮你完成校验　签发token最后响应　其实是封装了django自带的验证然后加了token再然后响应
    url(r'^authorizations/$', obtain_jwt_token),  
    # 用户详情
    url(r'^user/$', views.UserDetail.as_view()),  
    # 更新邮箱 
    url(r'^email/$', views.EmailView.as_view()),  
    url(r'^emails/verification/$', views.EmailVerifyView.as_view()),  
    url(r'^browse_histories/$', views.UserBrowserHistory.as_view()),  
]
router = routers.DefaultRouter()
router.register(r'addresses',views.AdressSetView,base_name='addresses')  # address好像也可以
urlpatterns += router.urls
# POST /addresses/ 新建  -> create
# PUT /addresses/<pk>/ 修改  -> update
# GET /addresses/  查询  -> list
# DELETE /addresses/<pk>/  删除 -> destroy
# PUT /addresses/<pk>/status/ 设置默认 -> status
# PUT /addresses/<pk>/title/  设置标题 -> title