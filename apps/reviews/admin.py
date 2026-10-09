from django.contrib import admin

from apps.reviews.models import Review


# Register your models here.

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["menu", "user", "rating", "created_at"]
    list_filter = ["rating"]
    search_fields = ["user__username", "comment"]
    readonly_fields = ["created_at"]

    list_select_related = ["menu", "user"]
