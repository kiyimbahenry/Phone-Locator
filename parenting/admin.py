from django.contrib import admin
from .models import (
    Child, PairingCode, AppRule, ScreenTimeRule,
    WebFilterLog, AppUsageLog, ParentingAlert,
)


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'age_group', 'is_paired', 'created_at')
    list_filter = ('age_group', 'is_paired', 'parental_consent_given')
    search_fields = ('name', 'parent__username')
    raw_id_fields = ('parent', 'device')
    readonly_fields = (
        'created_at', 'updated_at', 'paired_at', 'parental_consent_at',
    )


@admin.register(PairingCode)
class PairingCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'child', 'created_at', 'expires_at', 'used_at')
    list_filter = ('used_at',)
    search_fields = ('code', 'child__name')
    raw_id_fields = ('child',)


@admin.register(AppRule)
class AppRuleAdmin(admin.ModelAdmin):
    list_display = ('app_name', 'child', 'status', 'daily_limit_minutes')
    list_filter = ('status',)
    search_fields = ('app_name', 'app_identifier', 'child__name')
    raw_id_fields = ('child',)


@admin.register(ScreenTimeRule)
class ScreenTimeRuleAdmin(admin.ModelAdmin):
    list_display = (
        'child', 'weekday_limit_minutes', 'weekend_limit_minutes',
        'bedtime_start', 'bedtime_end', 'is_active',
    )
    list_filter = ('is_active',)
    raw_id_fields = ('child',)


@admin.register(WebFilterLog)
class WebFilterLogAdmin(admin.ModelAdmin):
    list_display = ('domain', 'child', 'category', 'blocked_at')
    list_filter = ('category',)
    search_fields = ('domain', 'child__name')
    raw_id_fields = ('child',)
    date_hierarchy = 'blocked_at'


@admin.register(AppUsageLog)
class AppUsageLogAdmin(admin.ModelAdmin):
    list_display = ('app_name', 'child', 'day', 'total_minutes')
    list_filter = ('day',)
    search_fields = ('app_name', 'app_identifier', 'child__name')
    raw_id_fields = ('child',)
    date_hierarchy = 'day'


@admin.register(ParentingAlert)
class ParentingAlertAdmin(admin.ModelAdmin):
    list_display = ('child', 'kind', 'occurred_at', 'is_read')
    list_filter = ('kind', 'is_read')
    search_fields = ('child__name', 'message')
    raw_id_fields = ('child',)
    date_hierarchy = 'occurred_at'
