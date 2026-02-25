from django.contrib import admin
from .models import Game, GameScreenshot
# Register your models here.
# admin.site.register(Game)

class ScreenshotInline(admin.TabularInline):
    model = GameScreenshot
    extra = 1

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    inlines = [ScreenshotInline]
    list_display = ["title", "price", "genre"]


admin.site.register(GameScreenshot)
