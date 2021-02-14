from rest_framework import serializers
from users.models import User
import re
from django_redis import get_redis_connection 
class CreateUserSerializer(serializers.ModelSerializer):
    """注册序列化器"""
    # 序列化字段['id', 'username','mobile'] 返回给前端的
    # 反序列化字段 ['username', 'password', 'password2', 'mobile', 'sms_code', 'allow']
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)  # 'true'
    class Meta:
        model = User
        # fields = "__all__"  #不能是所有的
        fields = ['id', 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow']  # id默认是只读的
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }
    def validate_moblie(self, value):
        """自定义验证手机号 注意：以后不管前端是否进行了验证　自己这里都要进行验证　并不是非要自己定义的才可以自定义验证规则"""
        if not re.match(r'1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式有误')
        return value
    
    def validate_allow(self, value):
        if value != 'true':
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, attrs):
        """使用联合校验来校验密码和验证码　arrts是前端传过来的所有数据　是一个字典"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('密码不一致')
        """校验验证码"""
        redis_conn = get_redis_connection("verify_codes")  # 获取redis连接对象 "verify_codes"数据库的名字
        mobile = attrs['mobile']
        redis_sms_code = redis_conn.get('sms_%s' % mobile)  # 通过键来取值
        # 注意　向redis数据库中存储数据都是以字符串形式进行存储的　但是取出来的数据都是bytes类型
        # 字符串取出来是bytes类型　列表取出来还是列表　但是列表中的字符串都是bytees类型
        # 过了5分钟了　验证码已经不存在了
        if redis_sms_code is None or redis_sms_code.decode() != attrs['sms_code']:
            # 注意先后顺序一定不能颠倒
            raise serializers.ValidationError('验证码错误')
        return attrs
    def create(self, validated_data):
        """重写create方法　modelserializer的create方法会将所有字段进行存储我们并不需要"""
        print("************************************************************************************************")
        print(validated_data)
        del validated_data['password2']  # validated_data是所有字段的数据　删掉后就只剩下username password mobile 存储到数据库中　但是
        del validated_data['sms_code']  # 问题是数据库中表有很多字段啊　只存这３个可以吗？
        del validated_data['allow']
        password = validated_data.pop('password')
        user = User(**validated_data)  # 关键字参数形式传递
        user.set_password(password)  # 把密码加密后再赋值给user的password属性
        user.save()
        return user


