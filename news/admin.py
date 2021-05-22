from django.contrib import admin
from .models import Category, Post, Comment, PostCategory, UserCategory


class PostCategoryInline(admin.TabularInline):
    model = PostCategory
    extra = 1


class UserCategoryInline(admin.TabularInline):
    model = UserCategory
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (PostCategoryInline, UserCategoryInline,)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = (PostCategoryInline,)


admin.site.register(Comment)
