from django.db import models
from utils.models import BaseModel  # 因为自己设置的原因导致导包错误也不会提示了　鱼与熊掌
# from users.models import User
from users.models import User
class OAuthQQUser(BaseModel):
    """新建一张表　用外键进行关联　避免冗余"""
    """
    QQ登录用户数据
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')  # 注意User是没有双引号的
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name
