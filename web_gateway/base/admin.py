import csv
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.html import format_html
from .models import Profile, History

# ─── Branding ─────────────────────────────────────────────────────────────────
admin.site.site_header  = "My Leaves"
admin.site.site_title   = "My Leaves Admin"
admin.site.index_title  = "Plant Disease Detection"

# ─── Actions ──────────────────────────────────────────────────────────────────
def export_history_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="predictions.csv"'
    writer = csv.writer(response)
    writer.writerow(['User', 'Result', 'Confidence', 'Date', 'Image'])
    for h in queryset:
        writer.writerow([h.user.username, h.result, '', h.created_at, h.image.name if h.image else ''])
    return response
export_history_csv.short_description = "Export selected as CSV"

# ─── History Admin ─────────────────────────────────────────────────────────────
@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display    = ('user', 'colored_result', 'image_thumbnail', 'created_at')
    list_filter     = ('created_at', 'user')
    search_fields   = ('user__username', 'result')
    readonly_fields = ('user', 'image', 'result', 'created_at')
    ordering        = ('-created_at',)
    date_hierarchy  = 'created_at'
    actions         = [export_history_csv]

    def colored_result(self, obj):
        color = '#2d6a4f' if 'healthy' in obj.result.lower() else '#dc3545'
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            color, obj.result
        )
    colored_result.short_description = 'Result'

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:48px; border-radius:4px;" />',
                obj.image.url
            )
        return "—"
    image_thumbnail.short_description = "Preview"

# ─── Profile Inline & Admin ───────────────────────────────────────────────────
class ProfileInline(admin.StackedInline):
    model              = Profile
    can_delete         = False
    verbose_name_plural = 'Profile'
    fields             = ('avatar', 'pay', 'ville')

class HistoryInline(admin.TabularInline):
    model           = History
    extra           = 0
    max_num         = 10
    readonly_fields = ('image', 'result', 'created_at')
    can_delete      = False
    ordering        = ('-created_at',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'ville', 'pay', 'avatar_preview')
    list_filter   = ('ville', 'pay')
    search_fields = ('user__username', 'ville', 'pay')

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="height:32px; width:32px; border-radius:50%;" />',
                obj.avatar.url
            )
        return "—"
    avatar_preview.short_description = "Avatar"

# ─── Extended User Admin ──────────────────────────────────────────────────────
class CustomUserAdmin(BaseUserAdmin):
    inlines      = (ProfileInline, HistoryInline)
    list_display = ('username', 'email', 'last_name', 'is_staff', 'is_superuser', 'date_joined')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
