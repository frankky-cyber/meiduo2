from django.shortcuts import render
from rest_framework.views import APIView
from random import randint
from django_redis import get_redis_connection
from libs.yuntongxun.sms import CCP
# from .. libs.yuntongxun.sms import CCP
from rest_framework.response import Response
import logging
from rest_framework import status
from .import constants
from celery_tasks.sms.tasks import send_sms_code


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
        # 创建redis管道(把多次redis操作放入管道中将一次性去执行，减少redis连接操作)
        pl = redis_conn.pipeline()
        #.把验证码存储到redis数据库
        # redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)  # 键，存储时间秒，值
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)  # 键，存储时间秒，值
        # 存储一个标记表示此手机号已经发送过短信 标记有效期为60s
        # redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)  # 键，存储时间秒，值
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)  # 键，存储时间秒，值
        # 执行管道
        pl.execute()
        # import time
        # time.sleep(5) #现在是单线程吗　就已经是多任务了吧　服务器自己解决的runserver或者你部署nginx等
        #利用容联云通讯发送短信验证码
        # CCP().send_template_sms(to, datas, temp_id) to是手机号　datas是列表[验证码,５] 5是分钟表示过期时间　还有短信内容的模板
        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], 1)
        # 触发异步任务，将异步任务添加到celery任务队列
        send_sms_code(mobile, sms_code)  # 这么做是错的　调用普通函数而已
        send_sms_code.delay(mobile, sms_code)  # 触发异步任务
        #响应
        return Response({'message':'ok'})
    