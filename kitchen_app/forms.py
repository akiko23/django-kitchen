from django.forms import (
    Form, 
    ChoiceField, 
    CharField, 
    IntegerField, 
    DecimalField, 
)
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Ingredient, RecipeCategory


class RegistrationForm(UserCreationForm):
    first_name = CharField(max_length=100, required=True)
    last_name = CharField(max_length=100, required=True)
    email = CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


# class CreateRecipeForm(Form):
#     name = CharField(max_length=100, required=True)
#     description = CharField(max_length=2000, required=True)
#     category = ChoiceField(choices=RecipeCategory.objects.all(), required=True)
#     ingredients = ChoiceField(choices=Ingredient.objects.all())

