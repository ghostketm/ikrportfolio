# ikrweb/admin.py
"""
Django admin configuration for Isaac Rono's portfolio backend.

Provides practical list displays, search, filters, and fieldsets so that
ordinary content updates (projects, skills, experience) never require
editing Python code or templates.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import About, Certification, Contact, Education, Experience, Project, Skill


# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display  = ['name', 'title', 'email', 'phone']
    search_fields = ['name', 'email']

    fieldsets = (
        ('Identity', {
            'fields': ('name', 'title', 'bio', 'profile_image', 'favicon')
        }),
        ('Contact & Location', {
            'fields': ('email', 'phone', 'location', 'website')
        }),
        ('Social Links', {
            'fields': ('linkedin', 'github', 'twitter', 'instagram', 'youtube'),
            'classes': ('collapse',),
        }),
        ('Documents', {
            'fields': ('resume',)
        }),
        ('M-Pesa Tipping', {
            'fields': ('mpesa_number', 'mpesa_name'),
            'classes': ('collapse',),
            'description': 'These values power the /tip/ page. Leave blank to hide tip fields.',
        }),
    )

    def has_add_permission(self, request):
        # Enforce singleton: prevent a second About record.
        return not About.objects.exists()


# ---------------------------------------------------------------------------
# Skill
# ---------------------------------------------------------------------------

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display   = ['name', 'category', 'level', 'icon', 'order']
    list_filter    = ['category', 'level']
    search_fields  = ['name', 'category']
    list_editable  = ['level', 'order', 'icon']
    ordering       = ['category', 'order', 'name']


# ---------------------------------------------------------------------------
# Experience
# ---------------------------------------------------------------------------

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display   = ['job_title', 'company', 'location', 'start_date', 'end_date', 'is_current']
    list_filter    = ['is_current']
    search_fields  = ['job_title', 'company', 'description']
    list_editable  = ['is_current']
    date_hierarchy = 'start_date'

    fieldsets = (
        ('Role', {
            'fields': ('job_title', 'company', 'location', 'is_current')
        }),
        ('Duration', {
            'fields': ('start_date', 'end_date'),
            'description': 'Leave end_date blank and tick is_current for the current role.',
        }),
        ('Details', {
            'fields': ('description',)
        }),
    )


# ---------------------------------------------------------------------------
# Education
# ---------------------------------------------------------------------------

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display   = ['degree', 'institution', 'field_of_study', 'start_date', 'end_date']
    list_filter    = ['start_date']
    search_fields  = ['institution', 'degree', 'field_of_study']
    date_hierarchy = 'start_date'

    fieldsets = (
        ('Institution', {
            'fields': ('institution', 'degree', 'field_of_study')
        }),
        ('Duration', {
            'fields': ('start_date', 'end_date')
        }),
        ('Details', {
            'fields': ('description',),
            'classes': ('collapse',),
        }),
    )


# ---------------------------------------------------------------------------
# Certification
# ---------------------------------------------------------------------------

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display   = ['name', 'issuer', 'issued_date', 'expiry_date']
    search_fields  = ['name', 'issuer', 'credential_id']
    list_filter    = ['issuer']

    fieldsets = (
        ('Certification', {
            'fields': ('name', 'issuer', 'credential_id', 'credential_url')
        }),
        ('Dates', {
            'fields': ('issued_date', 'expiry_date'),
            'description': 'Leave expiry_date blank for certifications that do not expire.',
        }),
    )


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display   = ['title', 'featured', 'is_published', 'tech_preview', 'created_at']
    list_filter    = ['featured', 'is_published', 'created_at']
    search_fields  = ['title', 'description', 'technologies']
    list_editable  = ['featured', 'is_published']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Project Identity', {
            'fields': ('title', 'slug', 'description', 'image')
        }),
        ('Technical Details', {
            'fields': ('technologies', 'github_url', 'live_url')
        }),
        ('Visibility', {
            'fields': ('featured', 'is_published'),
            'description': 'Featured projects appear on the home page. '
                           'Unpublished projects are hidden from all public pages.',
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Technologies')
    def tech_preview(self, obj):
        techs = obj.get_technologies_list()[:4]
        badges = ' '.join(
            f'<span style="background:#6c757d;color:#fff;padding:2px 6px;'
            f'border-radius:4px;font-size:11px;">{t}</span>'
            for t in techs
        )
        return format_html(badges)


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display   = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter    = ['is_read', 'created_at']
    search_fields  = ['name', 'email', 'subject', 'message']
    list_editable  = ['is_read']
    readonly_fields = ['name', 'email', 'subject', 'message', 'created_at']
    date_hierarchy  = 'created_at'

    def has_add_permission(self, request):
        """Contact submissions are created only by site visitors via the form."""
        return False