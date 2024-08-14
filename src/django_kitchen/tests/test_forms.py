"""Test forms."""

from django.contrib.auth.models import User
from django.test import TestCase

from kitchen_app.forms import (
    CreateCommentForm,
    CreateIngredientForm,
    CreateRecipeForm,
    RegistrationForm,
)
from kitchen_app.models import (
    Ingredient,
    IngredientCategory,
    Recipe,
    RecipeCategory,
)

PSWD2 = 'password2'
PSWD = 'pa$$word12345'
NAME = 'name'
PHONE = 'phone'


class FormTests(TestCase):
    """Test cases for form validations."""

    def test_registration_form_valid(self):
        """Test valid registration form."""
        form_data = {
            'username': 'new',
            'first_name': 'first',
            'last_name': 'last',
            'email': 'email@mail.ru',
            'password1': PSWD,
            'password2': PSWD,
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_invalid_username(self):
        """Test registration form with existing username."""
        User.objects.create_user(username='existinguser', password=PSWD)
        form_data = {
            'username': 'new',
            'first_name': 'first',
            'last_name': 'last',
            'email': 'email',
            'password1': PSWD,
            'password2': PSWD,
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_registration_form_password_mismatch(self):
        """Test registration form with password mismatch."""
        form_data = {
            'username': 'new',
            'first_name': 'first',
            'last_name': 'last',
            'email': 'email',
            'password1': PSWD,
            'password2': 'password54321',
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_create_recipe_form(self):
        """Test valid review creation form."""
        recipe_cat = RecipeCategory.objects.create(id=12, name='some_recipe_cat')
        ingredient_cat = IngredientCategory.objects.create(id=12, name='some_ingredient_cat')
        ingredient = Ingredient.objects.create(id=12, name='ing', price=123, category=ingredient_cat)
        form_data = {
            'name': 'Recipe1',
            'description': 'Just a sample recipe',
            'category': recipe_cat.id,
            'ingredients': [ingredient.id]
        }
        form = CreateRecipeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_create_recipe_form_invalid(self):
        """Test invalid review creation form."""
        ingredient_cat = IngredientCategory.objects.create(id=12, name='some_ingredient_cat')
        ingredient = Ingredient.objects.create(id=12, name='ing', price=123, category=ingredient_cat)
        form_data = {
            'name': 'Recipe1',
            'description': 'Just a sample recipe',
            'category': '21415',
            'ingredients': [ingredient.id]
        }

        form = CreateRecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)

    def test_create_ingredient_form(self):
        """Test valid review creation form."""
        ingredient_cat = IngredientCategory.objects.create(id=12, name='some_ingredient_cat')
        form_data = {
            'name': 'Ing1',
            'category': ingredient_cat.id,
            'price': 123
        }
        form = CreateIngredientForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_create_ingredient_form_invalid(self):
        """Test valid review creation form."""
        form_data = {
            'name': 'Ing1',
            'category': 12552,
            'price': 123
        }
        form = CreateIngredientForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_create_comment_form(self):
        """Test valid review creation form."""
        recipe = Recipe.objects.create(
            id=13,
            name='Recipe1',
            description='Just a sample recipe',
            category=RecipeCategory.objects.create(id=13, name='some_recipe_cat'),
            user=User.objects.create_user(username='recipe_creator', password=PSWD)
        )
        form_data = {
            'text': 'bla bla',
            'recipe': recipe.id,
            'user': User.objects.create_user(username='recipe_commentator', password=PSWD)
        }

        form = CreateCommentForm(data=form_data)
        form.fields['recipe'].choices = zip([recipe.id], [recipe])

        self.assertEqual(form.errors, {})
        self.assertTrue(form.is_valid())

    def test_create_comment_form_invalid(self):
        """Test valid review creation form."""
        form_data = {
            'text': 'bla bla',
            'recipe': '-12454',
            'user': User.objects.create_user(username='user', password=PSWD)
        }
        form = CreateCommentForm(data=form_data)
        self.assertFalse(form.is_valid())
