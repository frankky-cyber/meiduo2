from rest_framework import serializers
from users.models import User,Address
import re
from django_redis import get_redis_connection 
from rest_framework_jwt.settings import api_settings
from celery_tasks.email.tasks import send_verify_email
from goods.models import SKU
class CreateUserSerializer(serializers.ModelSerializer):
    """注册序列化器"""
    # 序列化字段['id', 'username','mobile'] 返回给前端的 　又加了token
    # 反序列化字段 ['username', 'password', 'password2', 'mobile', 'sms_code', 'allow']
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)  # 'true'
    token = serializers.CharField(label='token', read_only=True)  # 想返回给前端，要么source要么临时加一个
    class Meta:
        model = User
        # fields = "__all__"  #不能是所有的
        fields = ['id', 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow','token']  # id默认是只读的
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
                # 在没写自定义验证下，可以验证不能为空和最大最小字符数(在这个范围之内)
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
    
        del validated_data['password2']  # validated_data是校验过的所有字段的数据　删掉后就只剩下username password mobile 存储到数据库中　但是
        del validated_data['sms_code']  # 问题是数据库中表有很多字段啊　只存这３个可以吗？
        del validated_data['allow']
        password = validated_data.pop('password')
        user = User(**validated_data)  # 关键字参数形式传递
        user.set_password(password)  # 把密码加密后再赋值给user的password属性
        user.save()
        #这里加token的原理是什么呢？
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 生成payload函数的引用
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER   # 生成JWT

        payload = jwt_payload_handler(user)  # 根据user生成用户的载荷部分(字典)
        token = jwt_encode_handler(payload)  # 传入载荷生成完整的jwt
        user.token = token
        return user  # 返回模型类的实例对象干刚创建的那个啊

class UserDetailSerializer(serializers.ModelSerializer):
    """用户详情序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'email_active']

class EmailSerializer(serializers.ModelSerializer):
    """更改邮箱序列化器"""
    """校验的话不需要写了　自动帮我们校验的"""
    class Meta:
        model = User
        fields = ['id', 'email']
        # email字段必须要传值过来　一个字段有默认值或者允许为空的 'required':False 我们修改为True
        extra_kwargs = {
            'email':{
                'required':True
            }
        }
    def update(self, instance, validated_data):
        """重写此方法　目的不是为了修改而是借此时机发激活邮箱"""
        # super().update(instance, validated_data)  可以这么写　也可以自己写
        instance.email = validated_data.get('email')
        instance.save()
        # 将来在此写发邮件的功能　用异步的方式先给前端响应　让后台发邮件去
        # send_email()
        # http://www.meiduo.site:8080/success_verify_email.html?token=1  # token放与用户相关的信息最好让用户看不懂　加密一下设置过期时间
        # verify_url = generate_email_verify_url(instance) 封装成函数　放utils文件里　封装成方法也可以
        verify_url = instance.generate_email_verify_url() #将字典数据加密成看不懂的字符串
        send_verify_email.delay(instance.email, verify_url=verify_url)
        return instance

class UserAddressSerializer(serializers.ModelSerializer):
    """
    用户地址序列化器
    """
    # source那个是新增加的　注意区别　这个是替换
    province = serializers.StringRelatedField(read_only=True)  #自己重新定义了省市区字段　不用模型里面的　因为模型里面是外键　映射过来只有id
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    # required 表示前端务必传对应的字段的值过来不然会报错　默认也是true自己又指定一下也可以
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def validate_mobile(self, value):
        """
        验证手机号
        """
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self,validated_data):
        #现在的问题是如何获取user　在视图里面可以request.user来获取　serializer里面如何获取呢?
        # 注意我们继承的genericapiview他帮我们实现的　如果是apiview的话我们要传这个参数
        user = self.context['request'].user  
        validated_data['user'] = user
        instance = Address.objects.create(**validated_data)
        return instance

class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """
    class Meta:
        model = Address
        fields = ('title',)

class UserBrowserHistorySerializer(serializers.Serializer):
    """保存商品浏览记录序列化器"""
    sku_id = serializers.IntegerField(label='商品sku_id', min_value = 1)  # label是直接访问后端时填写表单时显示的　不是站点
    def validate_sku_id(self, value):
        """单独对sku_id进行校验　校验其是否存在"""
        try:
            SKU.objects.get(id= value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('sku_id无效')
        return value

    def create(self, validated_data):
        sku_id = validated_data.get('sku_id')
        # 获取用户对象
        user = self.context['request'].user
        # 创建redis连接对象
        redis_conn = get_redis_connection('history')
        # 创建redis管道
        pl = redis_conn.pipeline()
        # 先去重
        pl.lrem('history % d' % user.id,  0, sku_id)
        # 再添加到列表的开头
        pl.lpush('history % d' % user.id,  sku_id)
        # 再截取列表中的前５个元素
        pl.ltrim('history % d' % user.id, 0, 4)
        # 执行管道
        pl.execute()
        # 通常来说是要返回一个模型对象的　否则self.instance接受不到　serializer.data的时候会出问题的吧
        # return obj  为什么是validated_data
        return validated_data