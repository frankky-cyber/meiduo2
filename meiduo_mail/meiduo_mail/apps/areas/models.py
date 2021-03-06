from django.db import models

class Area(models.Model):
    """
    行政区划
    """
    #subs是隐式的字段　数据库中不会生成但可以根据它来查寻１对应的多有哪些
    name = models.CharField(max_length=20, verbose_name='名称')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True, verbose_name='上级行政区划')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural = '行政区划'

    def __str__(self):
        return self.name
