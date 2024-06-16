from django.forms import (
    Form,
    ChoiceField,
    MultipleChoiceField,
    CharField, IntegerField, Textarea
)
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Recipe, Ingredient, Comment


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
    category = ChoiceField(required=True)
    ingredients = MultipleChoiceField(required=True)

    class Meta:
        model = Recipe
        fields = ['name', 'description', 'category', 'ingredients']


class CreateIngredientForm(Form):
    name = CharField(max_length=100, required=True)
    category = ChoiceField(required=True)
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
