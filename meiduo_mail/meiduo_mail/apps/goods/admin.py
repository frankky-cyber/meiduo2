from django.contrib import admin
from goods import models
from celery_tasks.html.tasks import generate_static_list_search_html, generate_static_sku_detail_html
class GoodsCategoryAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        generate_static_list_search_html.delay()
        # generate_static_sku_detail_html.delay(obj.id) 不单单要监听这个模型的数据　详情页面（写死的东西比较多）９个模型都需要监听

    def delete_model(self, request, obj):
        obj.delete()
        generate_static_list_search_html.delay()

# @admin.register(models.SKU)
class SKUAdmin(admin.ModelAdmin):
    """商品模型站点管理类"""

    def save_model(self, request, obj, form, change):

        obj.save()  # 千万不要少了这一行,不然admin的保存就无效

        generate_static_sku_detail_html.delay(obj.id)


class SKUImageAdmin(admin.ModelAdmin):
    """商品图片模型站点管理类"""

    def save_model(self, request, obj, form, change):
        """

        :param request:
        :param obj: 图片模型对象
        :param form:
        :param change:
        :return:
        """
        obj.save()  # 千万不要少了这一行,不然admin的保存就无效

        sku = obj.sku  # 通过外键获取图片模型对象所关联的sku模型的id
        # 如果当前sku商品还没有默认图片,就给它设置一张默认图片
        if not sku.default_image_url:
            sku.default_image_url = obj.image.url

            generate_static_sku_detail_html.delay(sku.id)

    def delete_model(self, request, obj):
        obj.delete()
        sku = obj.sku  # 获取到图片模型对象关联的sku模型
        generate_static_sku_detail_html.delay(sku.id)

# Register your models here.
admin.site.register(models.GoodsCategory, GoodsCategoryAdmin)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU, SKUAdmin)
admin.site.register(models.SKUSpecification)
admin.site.register(models.SKUImage, SKUImageAdmin)