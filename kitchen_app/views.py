from typing import Any, Callable

from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.core.paginator import Paginator
from rest_framework import viewsets, permissions, authentication
from rest_framework.response import Response

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from rest_framework_swagger.views import get_swagger_view

from .models import Recipe, Ingredient, RecipeCategory, IngredientCategory, RecipeIngredient, Comment
from .forms import RegistrationForm, CreateRecipeForm
from .serializers import RecipeSerializer, IngredientSerializer, RecipeCategorySerializer, IngredientCategorySerializer, CommentSerializer


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

RecipeListView.create = lambda self, request: print("blas lbl")

def create_view(model_class, template, model_name, create_form = None):
    @login_required
    def view(request):
        target_id = request.GET.get('id', '')
        target_instance = model_class.objects.get(id=target_id) if target_id else None
        context = {
            model_name: target_instance,
        }

        if not request.user.is_authenticated:
            return redirect('homepage')
        
        if request.method == 'POST':
            form = create_form(request.POST)
            if not form.is_valid():
                context['errors'] = form.errors
            else:
                recipe = form.save()
                return redirect('homepage')
        return render(
            request,
            template,
            context,
        )
    return view

recipe_view = create_view(Recipe, 'entities/recipe.html', 'recipe', CreateRecipeForm)
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

PRIVATE_RESOURCES = (RecipeCategory, IngredientCategory, Ingredient)

def permission_by_model(model_class):
    class MyPermission(permissions.BasePermission):
        def has_permission(self, request, _):
            is_authenticated = bool(request.user and request.user.is_authenticated)
            
            if model_class in PRIVATE_RESOURCES and request.method in unsafe_methods:
                return is_authenticated and request.user.is_superuser
            return is_authenticated
    return MyPermission


def create_viewset(model_class, serializer):
    class ViewSet(viewsets.ModelViewSet):
        queryset = model_class.objects.all()
        serializer_class = serializer
        permission_classes = [permission_by_model(model_class)]
        authentication_classes = [authentication.TokenAuthentication]
                
    return ViewSet



RecipeCategoryViewSet = create_viewset(RecipeCategory, RecipeCategorySerializer)
IngredientCategoryViewSet = create_viewset(IngredientCategory, IngredientCategorySerializer)
IngredinetViewSet = create_viewset(Ingredient, IngredientSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permission_by_model(Recipe)]
    authentication_classes = [authentication.TokenAuthentication]

    def create(self, request):
        if self.request.method == "POST":
            data = request.data.copy()

            serializer = self.serializer_class(data=data)
            if not serializer.is_valid():
                with open('/home/akiko/loggg.txt', 'w') as f:
                    f.write(str(serializer.errors))
                return Response({'errors' : serializer.errors}, status=400)
            
            new_recipe = Recipe.objects.create(
                name=data['name'],
                description=data['description'],
                category=RecipeCategory(id=data['category']),
                user=User.objects.get(id=self.request.user.id),
            )

            RecipeIngredient.objects.bulk_create(
                [
                    RecipeIngredient(
                        recipe=new_recipe,
                        ingredient=Ingredient.objects.get(id=ing['ingredient_id']),
                        quantity=ing['quantity'],
                    )
                    for ing in data['ingredients']
                ]
            )
            
            return Response({'status' : 'ok'}, status=201)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permission_by_model(Comment)]
    authentication_classes = [authentication.TokenAuthentication]

    def create(self, request):
        if self.request.method == "POST":
            data = request.data.copy()

            serializer = self.serializer_class(data=data)
            if not serializer.is_valid():
                return Response({'errors' : serializer.errors}, status=400)
            
            Comment.objects.create(
                text=data['text'],
                recipe=Recipe.objects.get(id=data['recipe_id']),
                user=User.objects.get(id=self.request.user.id),
            )

            return Response({'status' : 'ok'}, status=201)


@login_required
def profile(request):
    client = User.objects.get(id=request.user.id)
    client_data = {
        'username': client.username,
        'first name': client.first_name,
        'last name': client.last_name,
        'email': client.email,
    }

    form = CreateRecipeForm()

    ingredients = Ingredient.objects.all()
    form.fields['ingredients'].choices = zip(range(len(ingredients)), ingredients)

    recipe_categories = RecipeCategory.objects.all()
    form.fields['category'].choices = zip(range(len(recipe_categories)), recipe_categories)


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
            'form': form
        }
    )


def unauthorized(request):
    return render(
        request,
        'pages/unauthorized.html',
    )
