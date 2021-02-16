from django.contrib.auth.backends import ModelBackend
import re
from users.models import User
def jwt_response_payload_handler(token, user=None, request=None):
    """重写jwt登录视图的构造响应数据函数，多追加user_id和username"""
    return{
        'token':token,
        'user_id':user.id,
        'username':user.username
    }

def get_user_by_account(account):
    """
    通过传入的账号动态的获取user 模型对象
    Arguments:account 可能是手机号也可能是用户名
    ---------
    Returns: user或者None
    -------
    """
    try:
        if re.match(r'1[3-9]\d{9}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user

class UsernameMobileAuthBackend(ModelBackend):
    # 修改django的认证类　为了实现多账号登录（同时支持用户名和手机号登录）
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 此时的username是前端传过来的数据　有可能是username也有可能是电话号
        # 获取到user (代码有很多封装成一个函数)
        user = get_user_by_account(username)
        # 查看前端传入的密码是否正确
        if user and user.check_password(password):
            # 返回user
            return user
