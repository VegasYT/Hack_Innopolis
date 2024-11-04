from django.contrib import admin
from .models import Employee, Aspect, ReviewCreator, Feedback, GeneralSummary, AspectSummary



@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id',)
    search_fields = ('id',)


@admin.register(Aspect)
class AspectAdmin(admin.ModelAdmin):
    list_display = ('id', 'text')
    search_fields = ('text',)


@admin.register(ReviewCreator)
class ReviewCreatorAdmin(admin.ModelAdmin):
    list_display = ('id',)
    search_fields = ('id',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'review_creator', 'employee', 'is_self_review', 'text_short')
    list_filter = ('is_self_review', 'review_creator', 'employee')
    search_fields = ('text', 'review_creator__id', 'employee__id')

    def text_short(self, obj):
        return obj.text[:50] + ('...' if len(obj.text) > 50 else '')
    text_short.short_description = "Текст отзыва"


@admin.register(GeneralSummary)
class GeneralSummaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'text_short')
    search_fields = ('text', 'employee__id')

    def text_short(self, obj):
        return obj.text[:50] + ('...' if len(obj.text) > 50 else '')
    text_short.short_description = "Общий вывод"


@admin.register(AspectSummary)
class AspectSummaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'aspect_name', 'employee', 'score', 'text_short')
    list_filter = ('score', 'employee')
    search_fields = ('text', 'employee__id')

    def text_short(self, obj):
        return obj.text[:50] + ('...' if len(obj.text) > 50 else '')
    text_short.short_description = "Текст аспекта"
