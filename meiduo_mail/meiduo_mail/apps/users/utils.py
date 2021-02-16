def jwt_response_payload_handler(token, user=None, request=None):
    """重写jwt登录视图的构造响应数据函数，多追加user_id和username"""
    return{
        'token':token,
        'user_id':user.id,
        'username':user.username
    }
