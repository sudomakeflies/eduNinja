# # personalized_learning/admin.py
# from django.contrib import admin
# from .models import LearningPath
# from .tasks import generate_recommendations, generate_feedback

# def trigger_recommendations(modeladmin, request, queryset):
#     generate_recommendations.delay()
#     modeladmin.message_user(request, "Recommendations generation triggered.")

# trigger_recommendations.short_description = "Generate recommendations for selected users"

# def trigger_feedback(modeladmin, request, queryset):
#     generate_feedback.delay()
#     modeladmin.message_user(request, "Feedback generation triggered.")

# trigger_feedback.short_description = "Generate feedback for selected users"

# class LearningPathAdmin(admin.ModelAdmin):
#     actions = [trigger_recommendations, trigger_feedback]

# admin.site.register(LearningPath, LearningPathAdmin)