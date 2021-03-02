#每一个任务有单独的一个包　每个包里面必须有一个名为tasks.py的文件　这个文件里写函数
#函数必须要装饰器进行装饰 　导入main文件下的celery_app
#在main文件添加这个任务 在列表里添加这个包
# 真正用的地方导入send_verify_email这个函数 用delay方式进行调用
from celery_tasks.main import celery_app
from django.core.mail import send_mail
from django.conf import settings
@celery_app.task(name='send_verify_email')  #起别名不然会很长
def send_verify_email(to_email, verify_url):
    """
    Arguments:to_email:收件人邮箱
    Arguments:verify_url:邮箱激活链接
    ---------
    Returns
    -------
    """
    subject = "美多商城邮箱验证"  #主题
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)
    # send_mail(subject:标题,message:普通邮件正文(字符串),  发件人，[收件人1,收件人2],html_message =超文本的邮件内容 )
    # 注意传参数的时候　最后一个要以关键字参数的形式传递
    send_mail(subject, '', settings.EMAIL_FROM, [to_email], html_message=html_message)