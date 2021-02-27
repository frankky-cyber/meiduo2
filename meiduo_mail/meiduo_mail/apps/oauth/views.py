from django.shortcuts import render
from rest_framework.views import APIView
from QQLoginTool.QQtool import OAuthQQ
from rest_framework.response import Response
from django.conf import settings  # 目前指的是dev文件,上线后指的是prod文件
from rest_framework import status
from oauth.models import OAuthQQUser
from rest_framework_jwt.settings import api_settings
from oauth.utils import generate_save_user_token
from oauth.serializer import QQAuthUserSerializer
import logging
logger = logging.getLogger('django')
# Create your views here.
class QQOauthURLView(APIView):
    """拼接好qq登录网址"""
    def get(self, request):
        # 提取前端传入的next参数记录用户从哪里进入到login界面
        # next = request.query_params.get('next') or '/'  # 如果为假则赋值为'/' 不用if来写
        next = request.query_params.get('next', '/')   #默认值的方式
        # # QQ登录参数　容易更改的放到配置文件
        # QQ_CLIENT_ID = '101474184'  # appid
        # QQ_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c'  # appkey
        # QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'  # 回调域名
        # 利用qq登录sdk
        # state记录来源
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        # 创建qq登录工具对象
        login_url = oauth.get_qq_url()
        # 调用它里面的方法　拼接好qq登录网址
        return Response({"login_url":login_url}) 


class QQAuthUserView(APIView):
    """QQ登录成功后的回调处理"""
    def get(self, request):
        # 获取前端传入的code
        code = request.query_params.get('code')
        if not code:  # 没有获取到code
            return Response({"message":"缺少code"},status=status.HTTP_400_BAD_REQUEST)
        # 创建qq登录工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            # 调用get_access_token()方法 用code向qq服务器发请求获得access_token 
            # 从后端发请求　不存在跨域（因为是浏览器的同源策略）
            access_token = oauth.get_access_token(code)
            # 调用get_open_id()方法 用code向服务器发请求获得openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.info(e)
            return Response({"message":"QQ服务器不可用"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # 查询数据库有没有这个openid
        try:
            oauthqqmodel = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 没有查到openid 创建一个新用户与openid绑定
            # OAuthQQUser.objects.create()
            #调用函数
            openid = generate_save_user_token(openid)  # 加密后的openid
            return Response({'access_token':openid})  # 响应给前端　前端名称写错了　加密响应给前端　让前端暂存一会绑定时再使用
        else:
            #查询到了openid 那么直接登录成功　给前端返回jwt
            user = oauthqqmodel.user  # 外键关联的用户对象
            # 手动生成token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 生成payload函数的引用
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER   # 生成JWT
            payload = jwt_payload_handler(user)  # 根据user生成用户的载荷部分(字典)　传用户对象过去生成对应的payload
            token = jwt_encode_handler(payload)  # 传入载荷生成完整的jwt
            return Response({
                'token':token,
                'username':user.username,
                'user_id':user.id
            })

    def post(self, request):
        """openid绑定用户接口"""
        #创建序列化器进行反序列化
        serializer = QQAuthUserSerializer(data = request.data)
        #调用is_valid()方法进行校验
        serializer.is_valid(raise_exception=True)
        #调用save方法
        user = serializer.save()  #在这里接 这里需要返回　一般是不需要返回的
        #生成ＪＷＴtoken
         # 手动生成token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 生成payload函数的引用
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER   # 生成JWT
        payload = jwt_payload_handler(user)  # 根据user生成用户的载荷部分(字典)
        token = jwt_encode_handler(payload)  # 传入载荷生成完整的jwt
        #响应
        return Response({
                'token':token,
                'username':user.username,
                'user_id':user.id
            })

    

    




