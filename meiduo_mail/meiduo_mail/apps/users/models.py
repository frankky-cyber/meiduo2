from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJSerializer,BadData
from django.conf import settings
# Create your models here.
class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱激活状态')  # 后追加的字段要设置默认值或者可以为空 
    class Meta: #配置数据库表名以及模型在admin站点显示的中文名
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def generate_email_verify_url(self):
        """生成邮箱激活链接"""
        # 创建加密序列化器
        serializer = TJSerializer(settings.SECRET_KEY, 3600*24)
        # 调用序列化器对象dumps方法进行加密
        data = {'user_id':self.id, 'email':self.email}
        token = serializer.dumps(data).decode()
        # 拼接激活url
        return 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token

    @staticmethod  # 修饰成为静态方法
    def check_verify_email_token(token):
        """对token解密并查询对应的user"""
        #创建序列话器对象
        serializer = TJSerializer(settings.SECRET_KEY, 3600*24)
        # 调用loads方法进行解密 解密的时如果过期的话或者数据有问题是会报异常的
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            id = data.get('user_id')
            email = data.get('email')
            try:
                user = User.objects.get(id=id,email=email)
            except User.DoesNotExist:
                return None
            else:
                return user
