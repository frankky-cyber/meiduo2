# celery启动文件
from celery import Celery
import os
# celery独立运行在django之外　找不到django的配置文件　这样配置后就能找到了
# 告诉celery如果需要django配置文件　应该去哪里加载
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mail.settings.dev")  # environ是字典 setdefault方法如果有这个键就什么都不做，没有这个就添加此键值对
# 1.创建celery实例对象
celery_app = Celery('meiduo')  # 客户端起别名
# 2.加载配置文件
celery_app.config_from_object('celery_tasks.config')
# 3.自动注册异步任务
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])