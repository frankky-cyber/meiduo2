from rest_framework import serializers
from oauth.utils import check_save_user_token
from django_redis import get_redis_connection
from oauth.models import User
from oauth.models import OAuthQQUser
class QQAuthUserSerializer(serializers.Serializer):
    """选择使用serializer而不是modelserializer　因为只进行反序列化而没有进行序列化　response那里写死了"""
    """openid绑定用户序列化器 不设置就是可读可写的"""
    access_token = serializers.CharField(label='操作凭证')  # openid
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(label='密码', max_length=20, min_length=8)
    sms_code = serializers.CharField(label='短信验证码')

    def validate(self, attrs):
        """用联合校验校验所有数据"""
        # 取出加密的openid并进行解密
        # access_token = attrs.get('access_token')
        access_token = attrs.pop('access_token')
        openid = check_save_user_token(access_token)
        if openid is None:
            raise serializers.ValidationError('openid无效')  #此时验证完openid　如果没报错证明openid没变
        #将openid添加到字典中　以备后续create使用
        attrs['openid'] = openid
        #校验验证码
        redis_conn = get_redis_connection("verify_codes")  # 获取redis连接对象 "verify_codes"数据库的名字
        mobile = attrs['mobile']
        redis_sms_code = redis_conn.get('sms_%s' % mobile)  # 通过键来取值
        # 注意　向redis数据库中存储数据都是以字符串形式进行存储的　但是取出来的数据都是bytes类型
        # 字符串取出来是bytes类型　列表取出来还是列表　但是列表中的字符串都是bytees类型
        # 过了5分钟了　验证码已经不存在了
        if redis_sms_code is None or redis_sms_code.decode() != attrs['sms_code']:
            # 注意先后顺序一定不能颠倒
            raise serializers.ValidationError('验证码错误')
        #校验手机号　是否注册过
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 用户没有注册过 选择什么也没做
            pass
        else:
            #调用校验密码方法对密码进行校验　返回值是true或者false
            if user.check_password(attrs['password']) is False:
                return serializers.ValidationError('密码错误')
            else:
                #用户已存在且密码也正确　把这个user对象存储到字典中　以备后期绑定时使用
                attrs['user'] = user
        return attrs

    def create(self,validated_data):  # 前面校验过的attrs(字典传过来了)
        # 判断validated_data中是否有user,如果有说明用户以存在
        user = validated_data.get('user')
        #如果没有　就创建一个新用户
        if user is None:
            user = User(username=validated_data.get('mobile'), mobile=validated_data.get('mobile'))
            user.set_password(validated_data.get('password'))
            user.save()
        # 将用户与openid进行绑定
        OAuthQQUser.objects.create(openid = validated_data.get('openid'),
        user = user)
        # 返回user
        return user