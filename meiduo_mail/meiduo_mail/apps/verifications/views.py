from django.shortcuts import render
from rest_framework.views import APIView
from random import randint
from django_redis import get_redis_connection
from libs.yuntongxun.sms import CCP
# from .. libs.yuntongxun.sms import CCP
from rest_framework.response import Response
import logging

logger = logging.getLogger('django')  # 用日志输出
# Create your views here.
class SMScodeView(APIView):
    """短信验证码"""
    def get(self, request, mobile):
        #1.生成验证码
        sms_code  = '%06d'  % randint(0, 999999)
        logger.info(sms_code)
        #2.创建redis连接对象
        redis_conn = get_redis_connection('verify_codes')  # 指定数据库名称连接到数据库
        #3.把验证码存储到redis数据库
        redis_conn.setex('sms_%  % mobile', 300, sms_code)  # 键，存储时间秒，值
        #4.利用容联云通讯发送短信验证码
        # CCP().send_template_sms(to, datas, temp_id) to是手机号　datas是列表[验证码,５] 5是分钟　还有短信内容的模板
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        #5.响应
        return Response({'message':'ok'})
    