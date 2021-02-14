from django.shortcuts import render
from rest_framework.generics import GenericAPIView,CreateAPIView
from users.serializers import CreateUserSerializer
# Create your views here.
class UserView(CreateAPIView):
    # 指定序列化器
    serializer_class = CreateUserSerializer
 