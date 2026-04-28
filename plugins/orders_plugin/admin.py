
from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    """Show order items inline on the order admin page"""
    model = OrderItem
    extra = 1
    fields = ['product_name', 'product', 'quantity', 'unit_price', 'subtotal']
    readonly_fields = ['subtotal']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'total_amount', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['id', 'customer__username']
    readonly_fields = ['total_amount', 'discount_applied', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('customer', 'status', 'priority')
        }),
        ('Financial Summary', {
            'fields': ('total_amount', 'discount_applied')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product_name', 'quantity', 'unit_price', 'subtotal']
    list_filter = ['order__status']
    search_fields = ['product_name', 'order__id']
    readonly_fields = ['subtotal']