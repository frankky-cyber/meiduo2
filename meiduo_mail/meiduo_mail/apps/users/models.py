from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJSerializer,BadData
from django.conf import settings
from meiduo_mail.utils.models import BaseModel
from areas.models import Area
# Create your models here.
class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱激活状态')  # 后追加的字段要设置默认值或者可以为空 
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='默认地址')
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

class Address(BaseModel):
    """
    用户地址
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    # province = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省') # 效果是一样的，不过下面的不需要导包了
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'  # 数据库中表的名称
        verbose_name = '用户地址' # admin下
        verbose_name_plural = verbose_name # admin下
        ordering = ['-update_time'] # 排序按照什么来排  和数据库中表怎么排没关系　传过去的queryset里面的每一个对象的顺序　