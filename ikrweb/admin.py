# ikrweb/admin.py
from django.contrib import admin
from .models import Project, About, Skill, Contact, Education

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'featured', 'created_at', 'updated_at']
    list_filter = ['featured', 'created_at', 'technologies']
    search_fields = ['title', 'description', 'technologies']
    list_editable = ['featured']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'image', 'featured')
        }),
        ('Technical Details', {
            'fields': ('technologies', 'github_url', 'live_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'email']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'title', 'bio', 'profile_image')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'location')
        }),
        ('Social Links', {
            'fields': ('linkedin', 'github', 'twitter')
        }),
        ('Documents', {
            'fields': ('resume',)
        })
    )

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'category']
    list_filter = ['level', 'category']
    search_fields = ['name', 'category']
    list_editable = ['level']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'subject']
    readonly_fields = ['created_at']
    
    def has_add_permission(self, request):
        return False
    
@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['institution', 'degree', 'start_date', 'end_date']
    list_filter = ['start_date', 'end_date']
    search_fields = ['institution', 'degree', 'field_of_study']
    list_editable = ['end_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('institution', 'degree', 'field_of_study', 'start_date')
        }),
        ('Advanced Information', {
            'fields': ('end_date', 'description')
        })
    )