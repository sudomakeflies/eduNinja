from django.contrib import admin
from .models import (
    LearningStyle, Competency, StudentCompetency,
    LearningPath, LearningResource, LearningActivity,
    ChatSession, ChatMessage, CompetencyAssessment
)

@admin.register(LearningStyle)
class LearningStyleAdmin(admin.ModelAdmin):
    list_display = ('student', 'get_dominant_style', 'last_updated')
    search_fields = ('student__username',)
    readonly_fields = ('last_updated',)

@admin.register(Competency)
class CompetencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'description')
    search_fields = ('name', 'description')
    list_filter = ('parent',)

@admin.register(StudentCompetency)
class StudentCompetencyAdmin(admin.ModelAdmin):
    list_display = ('student', 'competency', 'level', 'last_assessed')
    search_fields = ('student__username', 'competency__name')
    list_filter = ('level', 'last_assessed')
    readonly_fields = ('last_assessed',)

@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ('student', 'competency', 'current_level', 'target_level', 'is_active')
    search_fields = ('student__username', 'competency__name')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at', 'last_updated')

    def get_progress(self, obj):
        return f"{obj.get_progress():.1f}%"
    get_progress.short_description = 'Progress'

@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'competency', 'difficulty_level', 'estimated_duration')
    search_fields = ('title', 'description', 'competency__name')
    list_filter = ('content_type', 'difficulty_level', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(LearningActivity)
class LearningActivityAdmin(admin.ModelAdmin):
    list_display = ('student', 'resource', 'progress', 'started_at', 'completed_at')
    search_fields = ('student__username', 'resource__title')
    list_filter = ('started_at', 'completed_at')
    readonly_fields = ('started_at',)

    def get_resource_type(self, obj):
        return obj.resource.get_content_type_display()
    get_resource_type.short_description = 'Resource Type'

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('student', 'created_at', 'last_interaction', 'get_message_count')
    search_fields = ('student__username',)
    list_filter = ('created_at', 'last_interaction')
    readonly_fields = ('created_at', 'last_interaction')

    def get_message_count(self, obj):
        return obj.messages.count()
    get_message_count.short_description = 'Messages'

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'is_student', 'content_preview', 'timestamp')
    search_fields = ('content', 'session__student__username')
    list_filter = ('is_student', 'timestamp')
    readonly_fields = ('timestamp',)

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'

@admin.register(CompetencyAssessment)
class CompetencyAssessmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'competency', 'score', 'completed_at')
    search_fields = ('student__username', 'competency__name')
    list_filter = ('completed_at', 'score')
    readonly_fields = ('completed_at',)

# Customize admin site header and title
admin.site.site_header = 'Personalized Learning Administration'
admin.site.site_title = 'Learning Management'
admin.site.index_title = 'Administration Dashboard'
