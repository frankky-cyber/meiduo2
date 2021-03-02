from django.shortcuts import render
from rest_framework.generics import GenericAPIView,CreateAPIView,RetrieveAPIView,UpdateAPIView
from rest_framework.views import APIView
from users.serializers import CreateUserSerializer,UserDetailSerializer,EmailSerializer
from users.models import User
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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

class UserDetail(RetrieveAPIView):
    serializer_class = UserDetailSerializer
    # queryset = User.objects.all() 以前是这样　指定queryset然后根据pk去查找　可是这种方法不是很好　需要去数据库中查找效率低　我们不用这种
    permission_classes = [IsAuthenticated] #指定权限　只有通过认证的用户才能访问当前视图

    def get_object(self):
        """重写get_object方法　返回要展示的用户模型对象"""
        return self.request.user  # 经过认证之后的　是哪一个用户　是否需要自己写认证类？

class EmailView(UpdateAPIView):
    """更新邮箱"""
    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        """重写get_object方法　返回要展示的用户模型对象"""
        return self.request.user 