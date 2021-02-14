from django.conf.urls import url
from users import views
urlpatterns = [
    #注册用户
    url(r'^users/$', views.UserView.as_view()),
]