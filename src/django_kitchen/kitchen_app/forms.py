from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import (
    CharField,
    ChoiceField,
    Form,
    IntegerField,
    ModelChoiceField,
    ModelMultipleChoiceField,
)

from .models import (
    Comment,
    Ingredient,
    IngredientCategory,
    Recipe,
    RecipeCategory,
)


class RegistrationForm(UserCreationForm):
    first_name = CharField(max_length=100, required=True)
    last_name = CharField(max_length=100, required=True)
    email = CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class CreateRecipeForm(Form):
    name = CharField(max_length=100, required=True)
    description = CharField(max_length=2000, required=True)
    category = ModelChoiceField(
        queryset=RecipeCategory.objects.all(),
        required=True
    )
    ingredients = ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        required=True,
    )

    class Meta:
        model = Recipe
        fields = ['name', 'description', 'category', 'ingredients']


class CreateIngredientForm(Form):
    name = CharField(max_length=100, required=True)
    category = ModelChoiceField(
        queryset=IngredientCategory.objects.all(),
        required=True
    )
    price = IntegerField(required=True)

    class Meta:
        model = Ingredient
        fields = ['name', 'category', 'price']


class CreateCommentForm(Form):
    text = CharField()
    recipe = ChoiceField(required=True)

    class Meta:
        model = Comment
        fields = ['text', 'recipe']
