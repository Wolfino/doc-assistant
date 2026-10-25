from django.contrib import admin

from .models import Manual, Section


class SectionInline(admin.StackedInline):
    model = Section
    extra = 1


@admin.register(Manual)
class ManualAdmin(admin.ModelAdmin):
    list_display = ["title", "created_at"]
    inlines = [SectionInline]