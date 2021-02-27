from django.conf.urls import url
from oauth.views import QQOauthURLView,QQAuthUserView
urlpatterns = [
    # 拼接qq登录url
    url(r"^qq/authorization/$", QQOauthURLView.as_view()),
    #qq登录后的回调
    url(r"^qq/user/$", QQAuthUserView.as_view()),
    
]

