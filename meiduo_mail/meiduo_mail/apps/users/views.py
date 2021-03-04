from django.shortcuts import render
from rest_framework.generics import GenericAPIView,CreateAPIView,RetrieveAPIView,UpdateAPIView
from rest_framework.views import APIView
from users.serializers import CreateUserSerializer,UserDetailSerializer,EmailSerializer
from users.models import User
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
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

class EmailVerifyView(APIView):  # 没用啥序列化器啥的就简单的apiview就可以了
    """激活用户邮箱"""
    def get(self, request):
        # 获取前端以查询字符串方式传过来的token
        token = request.query_params.get('token')
        #将token解密　并查询对应的user对象 里面是有逻辑的
        user = User.check_verify_email_token(token)
        
        #修改user对象的email_active为True
        if user is None:
            return Response({'message':'激活失败'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 项目中所有文件(views,serlizer,utils,models)都支持python语法对模型对象的相关操作
        # 模型对象.属性赋值(对数据库中的某个对象的值进行修改)　从表里面查找某一个用户或者查询集　创建一个新的用户并保存等等
        # user.check_password set_password等等 user = oauthqqmodel.user  # 外键关联的用户对象等等return Response({
            #     'token':token,
            #     'username':user.username,
            #     'user_id':user.id
            # })
        # 创建用户的时候要注意user.set_password(validated_data.get('password'))
            # user.save()　密码这里比较特殊　不能objects.create()
        #还要注意user = User.objects.get(id=id,email=email)
            # except User.DoesNotExist:
        user.email_active = True
        user.save()
        # 响应
        return Response({'message':'ok'})