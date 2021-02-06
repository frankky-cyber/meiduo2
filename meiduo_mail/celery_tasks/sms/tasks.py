#  编写异步任务代码　就是一个函数而已
from .yuntongxun.sms import CCP
from .import constants
from..main import celery_app

@celery_app.task(name='send_sms_code')  # 使用装饰器注册任务 给任务起别名
def  send_sms_code(mobile, sms_code):
    """
    发送短信的celery异步任务
    Arguments:mobie:手机号
    Arguments:sms_code:验证码
    ---------

    """
    CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], 1)  