from django.contrib import admin
from django.utils.html import format_html
from .models import BlockType, DeliveryZone, Order

@admin.register(BlockType)
class BlockTypeAdmin(admin.ModelAdmin):
    # 'display_image' itakuonyesha picha ndogo kwenye list
    list_display = ('display_image', 'name', 'price_per_block', 'strength_rating')
    list_editable = ('price_per_block',) # Unaweza kubadili bei hapa hapa bila kufungua bidhaa
    search_fields = ('name',)

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 5px;" />', obj.image.url)
        return "No Image"
    
    display_image.short_description = 'Picha'

@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ('zone_name', 'delivery_fee')
    list_editable = ('delivery_fee',)
    search_fields = ('zone_name',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'block_type', 'quantity', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'delivery_zone', 'created_at')
    search_fields = ('id', 'block_type__name')
    # Inafanya oda ziweze kusomeka tu (Read Only) ili kuzuia bosi asibadili bei ya oda iliyokwisha fanyika
    readonly_fields = ('total_price', 'created_at')