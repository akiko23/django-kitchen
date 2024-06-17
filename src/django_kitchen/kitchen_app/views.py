from typing import Any, Callable

from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.core.paginator import Paginator
from rest_framework import viewsets, permissions, authentication
from rest_framework.response import Response

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token

from .models import Recipe, Ingredient, RecipeCategory, IngredientCategory, RecipeIngredient, Comment
from .forms import RegistrationForm, CreateRecipeForm, CreateIngredientForm, CreateCommentForm
from .serializers import RecipeSerializer, IngredientSerializer, RecipeCategorySerializer, IngredientCategorySerializer, \
    CommentSerializer


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
        ordering = ['id']

        def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
            context = super().get_context_data(**kwargs)
            instances = model_class.objects.all()
            paginator = Paginator(instances, 10)
            page = self.request.GET.get('page')
            page_obj = paginator.get_page(page)
            context[f'{plural_name}_list'] = page_obj
            return context

    return View


def recipe_list_view(request):
    target_category_id = request.GET.get('category_id', '')

    category_inst = RecipeCategory.objects.get(id=target_category_id)

    target_instances = Recipe.objects.filter(category_id=target_category_id) if target_category_id else None
    context = {
        "recipes_list": target_instances,
        "category": category_inst
    }

    if not request.user.is_authenticated:
        return redirect('homepage')

    return render(
        request,
        "collections/recipes.html",
        context,
    )


def ingredient_list_view(request):
    target_category_id = request.GET.get('category_id', '')

    category_inst = IngredientCategory.objects.get(id=target_category_id)

    target_instances = Ingredient.objects.filter(category_id=target_category_id) if target_category_id else None
    context = {
        "ingredients_list": target_instances,
        "category": category_inst
    }

    if not request.user.is_authenticated:
        return redirect('homepage')

    return render(
        request,
        "collections/ingredients.html",
        context,
    )


RecipeCategoryListView = create_listview(RecipeCategory, 'collections/recipe_categories.html', 'recipe_categories')
IngredientCategoryListView = create_listview(IngredientCategory, 'collections/ingredient_categories.html',
                                             'ingredient_categories')
IngredientListView = create_listview(Ingredient, 'collections/ingredients.html', 'ingredients')


def recipe_view(request):
    target_id = request.GET.get('id', '')
    target_instance = Recipe.objects.get(id=target_id) if target_id else None
    context = {
        'recipe': target_instance,
    }

    if not request.user.is_authenticated:
        return redirect('homepage')

    auth_token = Token.objects.get_or_create(user=request.user)
    context['auth_token'] = auth_token[0].key

    if request.method == 'POST':
        form = CreateRecipeForm(request.POST)
        form.full_clean()
        data = form.cleaned_data

        new_recipe = Recipe.objects.create(
            name=data['name'],
            description=data['description'],
            category=data['category'],
            user=User.objects.get(id=request.user.id),
        )

        try:
            RecipeIngredient.objects.bulk_create(
                [
                    RecipeIngredient(
                        recipe=new_recipe,
                        ingredient=ing,
                        quantity=1,
                    )
                    for ing in data['ingredients']
                ]
            )
        except Ingredient.DoesNotExist:
            pass

        return redirect('profile')

    context['recipe_ingredients'] = target_instance.ingredients.all()

    comment_form = CreateCommentForm()
    comment_form.fields['recipe'].choices = zip([target_instance.id], [target_instance])
    context['comment_form'] = comment_form
    context['comments'] = Comment.objects.filter(recipe_id=target_instance.id)
    return render(
        request,
        'entities/recipe.html',
        context,
    )


def ingredient_view(request):
    target_id = request.GET.get('id', '')
    target_instance = Ingredient.objects.get(id=target_id) if target_id else None
    context = {
        'ingredient': target_instance,
    }

    if not request.user.is_authenticated:
        return redirect('homepage')

    auth_token = Token.objects.get_or_create(user=request.user)
    context['auth_token'] = auth_token[0].key

    if request.method == 'POST':
        form = CreateIngredientForm(request.POST)
        form.full_clean()
        data = form.cleaned_data

        new_ingredient = Ingredient.objects.create(
            name=data['name'],
            category=data['category'],
            price=data['price'],
        )

        context['ingredient'] = new_ingredient
        return render(
            request,
            'entities/ingredient.html',
            context
        )

    return render(
        request,
        'entities/ingredient.html',
        context,
    )


def comment_view(request):
    if request.method == 'POST':
        form = CreateCommentForm(request.POST)

        data = form.data

        target_recipe = Recipe.objects.get(id=data['recipe'])
        Comment.objects.create(
            text=data['text'],
            user=request.user,
            recipe=target_recipe,
        )

        return redirect(
            'profile'
        )


def register(request):
    errors = ''
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
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
IngredientViewSet = create_viewset(Ingredient, IngredientSerializer)


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
                return Response({'errors': serializer.errors}, status=400)

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

            return Response({'status': 'ok'}, status=201)


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
                return Response({'errors': serializer.errors}, status=400)

            Comment.objects.create(
                text=data['text'],
                recipe=Recipe.objects.get(id=data['recipe_id']),
                user=User.objects.get(id=self.request.user.id),
            )

            return Response({'status': 'ok'}, status=201)


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
    form.fields['ingredients'].queryset = Ingredient.objects.all()
    form.fields['category'].queryset = RecipeCategory.objects.all()

    ing_form = CreateIngredientForm()
    ing_form.fields['category'].queryset = IngredientCategory.objects.all()

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
            'form': form,
            'ing_form': ing_form
        }
    )


def unauthorized(request):
    return render(
        request,
        'pages/unauthorized.html',
    )
