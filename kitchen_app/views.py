from typing import Any, Callable
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.core.paginator import Paginator
from rest_framework import viewsets, permissions, authentication
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from rest_framework_swagger.views import get_swagger_view


from .models import Recipe, Ingredient
from .forms import RegistrationForm
from .serializers import RecipeSerializer, IngredientSerializer


def check_auth(view: Callable) -> Callable:
    def new_view(request):
        if not (request.user and request.user.is_authenticated):
            return redirect('unauthorized')
        return view(request)
    return new_view

def home_page(request):
    return render(
        request,
        'index.html',
        context={
            'recipes': Recipe.objects.count(),
            'ingredients': Ingredient.objects.count(),
        }
    )

def create_listview(model_class, template, plural_name):
    class View(LoginRequiredMixin, ListView):
        model = model_class
        template_name = template
        paginate_by = 10
        context_object_name = plural_name

        def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
            context = super().get_context_data(**kwargs)
            instances = model_class.objects.all()
            paginator = Paginator(instances, 10)
            page = self.request.GET.get('page')
            page_obj = paginator.get_page(page)
            context[f'{plural_name}_list'] = page_obj
            return context
    return View

RecipeListView = create_listview(Recipe, 'collections/recipes.html', 'recipes')
IngredientListView = create_listview(Ingredient, 'collections/ingredients.html', 'ingredients')

def create_view(model_class, template, model_name):
    @login_required
    def view(request):
        target_id = request.GET.get('id', '')
        target_instance = model_class.objects.get(id=target_id) if target_id else None
        context = {
            model_name: target_instance,
        }

        if request.user.is_authenticated:
            return render(
                request,
                template,
                context,
            )
        return redirect('homepage')
    return view

recipe_view = create_view(Recipe, 'entities/recipe.html', 'recipe')
ingredient_view = create_view(Ingredient, 'entities/ingredient.html', 'ingredient')

def register(request):
    errors = ''
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('homepage')
        else:
            errors = form.errors
    else:
        form = RegistrationForm()
    return render(
        request,
        'registration/register.html',
        {'form': form, 'errors': errors}
    )

safe_methods = 'GET', 'HEAD', 'OPTIONS'
unsafe_methods = 'POST', 'DELETE', 'PUT'

class MyPermission(permissions.BasePermission):
    def has_permission(self, request, _):
        if request.method in safe_methods:
            return bool(request.user and request.user.is_authenticated)
        elif request.method in unsafe_methods:
            return bool(request.user and request.user.is_superuser)
        return False

def create_viewset(model_class, serializer):
    class ViewSet(viewsets.ModelViewSet):
        queryset = model_class.objects.all()
        serializer_class = serializer
        permission_classes = [MyPermission]
        authentication_classes = [authentication.TokenAuthentication]

    return ViewSet

RecipeViewSet = create_viewset(Recipe, RecipeSerializer)
IngredinetViewSet = create_viewset(Ingredient, IngredientSerializer)

@login_required
def profile(request):
    client = User.objects.get(id=request.user.id)
    client_data = {
        'username': client.username,
        'first name': client.first_name,
        'last name': client.last_name,
        'email': client.email,
    }
    return render(
        request,
        'pages/profile.html',
        {
            'client_data': client_data,
            'client_recipes': Recipe.objects.raw(
                """
                SELECT * FROM recipes
                WHERE user_id=%s
                """,
                [client.id],
            ),
        }
    )

# @login_required
# def buy(request):
#     client = User.objects.get(email=request.user.email)
#     recipe_id = request.GET.get('id', None)
#     recipe = Recipe.objects.get(id=recipe_id) if recipe_id else None

#     return render(
#         request,
#         'pages/buy.html',
#         {
#             'book': book,
#             'money': client.money if client else None,
#         }
#     )


def unauthorized(request):
    return render(
        request,
        'pages/unauthorized.html',
    )