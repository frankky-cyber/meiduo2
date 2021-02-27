from itsdangerous import TimedJSONWebSignatureSerializer as TJSSSerializer,BadData
from django.conf import settings  # 使用dev文件
def generate_save_user_token(openid):
    """对openid进行加密"""
    # 创建加密的序列化器对象 密钥使用配置文件中的密钥 过期时间600秒 600这里可以使用常量代替
    serializer = TJSSSerializer(settings.SECRET_KEY, 600)
    #调用dumps方法(JSON字典)进行加密
    data = {'openid':openid}
    token = serializer.dumps(data)  # 加密后的数据　默认是bytes类型
    # 将加密后的openid返回
    return token.decode()

def check_save_user_token(access_token):
    """对传过来的加密的openid进行解密"""
    # 创建加密的序列化器对象 密钥使用配置文件中的密钥 过期时间600秒 
    serializer = TJSSSerializer(settings.SECRET_KEY, 600)
    #调用loads方法进行解密
    try:
        data = serializer.loads(access_token)
    except BadData:  #因为过期或者什么解不开而导致异常
        return None
    else:
        return data.get('openid')


    
