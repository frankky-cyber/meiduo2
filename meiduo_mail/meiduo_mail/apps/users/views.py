from django.shortcuts import render
from rest_framework.generics import GenericAPIView,CreateAPIView
from rest_framework.views import APIView
from users.serializers import CreateUserSerializer
from users.models import User
from rest_framework.response import Response
# Create your views here.
class UserView(CreateAPIView):
    # 指定序列化器
    serializer_class = CreateUserSerializer

class UsernameCountView(APIView):
    """判断用户是否已注册"""
    def get(self, request, username):
        # 查询user表
        count = User.objects.filter(username=username).count()
        # 包装响应数据 username不一定用的上我们也传回去
        data = {
            'username':username,
            'count':count
        }
        # 响应
        return Response(data)

class MobileCountView(APIView):
    """判断手机号是否已注册"""
    def get(self, request, mobile):
        # 查询user表
        count = User.objects.filter(mobile=mobile).count()
        # 包装响应数据 
        data = {
            'mobile':mobile,
            'count':count
        }
        # 响应
        return Response(data)
