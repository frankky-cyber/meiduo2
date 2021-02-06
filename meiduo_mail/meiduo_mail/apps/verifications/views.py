from django.shortcuts import render
from rest_framework.views import APIView
from random import randint
from django_redis import get_redis_connection
from libs.yuntongxun.sms import CCP
# from .. libs.yuntongxun.sms import CCP
from rest_framework.response import Response
import logging
from rest_framework import status

logger = logging.getLogger('django')  # 用日志输出
# Create your views here.
class SMScodeView(APIView):
    """短信验证码"""
    def get(self, request, mobile):
        #创建redis连接对象
        redis_conn = get_redis_connection('verify_codes')  # 指定数据库名称连接到数据库
        # 从redis中获取标记
        send_flag = redis_conn.get('send_flag_%s' % mobile)  # 取不到也不会报错　是none 
        if send_flag:  # 如果取到了标记说明此手机号频繁发送
            return Response({'message':'手机频繁发送短信'}, status=status.HTTP_400_BAD_REQUEST)
        # 生成验证码
        sms_code  = '%06d'  % randint(0, 999999)
        logger.info(sms_code)
        #.把验证码存储到redis数据库
        redis_conn.setex('sms_%s' % mobile, 300, sms_code)  # 键，存储时间秒，值
        # 存储一个标记表示此手机号已经发送过短信 标记有效期为60s
        redis_conn.setex('send_flag_%s' % mobile, 60, 1)  # 键，存储时间秒，值
        #利用容联云通讯发送短信验证码
        # CCP().send_template_sms(to, datas, temp_id) to是手机号　datas是列表[验证码,５] 5是分钟　还有短信内容的模板
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        #响应
        return Response({'message':'ok'})
    