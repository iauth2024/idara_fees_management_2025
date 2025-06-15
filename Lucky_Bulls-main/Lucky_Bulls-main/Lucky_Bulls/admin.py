from django.contrib import admin
from .models import TradingAccount, Screener, MonitorControl

# Register TradingAccount with custom admin class
@admin.register(TradingAccount)
class TradingAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'client_id', 'is_master', 'is_child', 'restrict_login')
    list_filter = ('is_master', 'is_child')
    search_fields = ('name', 'client_id')

    # Add the restrict_login field to the admin form
    fieldsets = (
        (None, {
            'fields': ('name', 'client_id', 'token', 'is_master', 'is_child', 'parent_account', 'multiplier', 'allowed_ips', 'restrict_login')
        }),
    )

# Register Screener with custom admin class
@admin.register(Screener)
class ScreenerAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)

# Register MonitorControl with custom admin class
@admin.register(MonitorControl)
class MonitorControlAdmin(admin.ModelAdmin):
    list_display = ('is_active', 'updated_at')
    list_editable = ('is_active',)
    list_display_links = ('updated_at',)  # Make 'updated_at' the clickable link instead of 'is_active'