from django.conf.urls import url
from verifications import views
urlpatterns = [
    #发短信
    url(r'^smscode/(?P<mobile>1[3-9]\d{9})/$', views.SMScodeView.as_view()),
]

