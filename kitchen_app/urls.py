from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView


from . import views


router = DefaultRouter()
router.register(r'recipes', views.RecipeViewSet)
router.register(r'ingredients', views.IngredinetViewSet)

urlpatterns = [
    path('', views.home_page, name='homepage'),
    path('recipes/', views.RecipeListView.as_view(), name='recipes'),
    path('recipe/', views.recipe_view, name='recipe'),
    path('ingredients/', views.IngredientListView.as_view(), name='ingredients'),
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
]
