from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.authtoken import views as drf_views
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'recipes', views.RecipeViewSet, basename='api-recipes')
router.register(r'ingredients', views.IngredientViewSet)
router.register(r'recipe-categories', views.RecipeCategoryViewSet)
router.register(r'ingredient-categories', views.IngredientCategoryViewSet)
router.register(r'comments', views.CommentViewSet)

urlpatterns = [
    path('', views.home_page, name='homepage'),
    path('recipes/', views.recipe_list_view, name='recipes'),
    path('recipe-categories/', views.RecipeCategoryListView.as_view(), name='recipe_categories'),
    path('recipe/', views.recipe_view, name='recipe'),
    path('comment/', views.comment_view, name='comment'),
    path('ingredient-categories/', views.IngredientCategoryListView.as_view(), name='ingredient_categories'),
    path('ingredients/', views.ingredient_list_view, name='ingredients'),
    path('ingredient/', views.ingredient_view, name='ingredient'),
    path('register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include(router.urls), name='api'),
    path('profile/', views.profile, name='profile'),
    path(
        "swagger-ui/",
        TemplateView.as_view(
            template_name="swagger-ui.html",
            extra_context={"schema_url": "openapi-schema"},
        ),
        name="swagger-ui",
    ),
    path('api/token-auth/', drf_views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls')),
]
