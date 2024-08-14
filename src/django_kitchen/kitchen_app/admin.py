from django.contrib import admin

from .models import (
    Comment,
    Ingredient,
    IngredientCategory,
    Recipe,
    RecipeCategory,
    RecipeIngredient,
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    model = Recipe
    inlines = (RecipeIngredientInline, )
    readonly_fields = ("created_at", )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    model = Comment
    readonly_fields = ("published_on", )


admin.site.register([
    Ingredient,
    RecipeIngredient,
    RecipeCategory,
    IngredientCategory,
])

