from django.contrib.auth.models import User
from django.test import Client, TestCase
from rest_framework import status

from kitchen_app.models import (
    Ingredient,
    IngredientCategory,
    Recipe,
    RecipeCategory,
)


class HomepageViewTest(TestCase):
    url = ""

    def setUp(self):
        self.client = Client()

        self.user = User(username='user', password='user')
        self.user.save()

        self.client.force_login(user=self.user)

    def test_get_homepage(self):
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_200_OK)


class ProfileViewTest(TestCase):
    url = "/profile/"

    def setUp(self):
        self.client = Client()

        self.user = User(username='user', password='user')
        self.user.save()

        self.client.force_login(user=self.user)

    def test_get_profile(self):
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_200_OK)

        # Client not authenticated
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_302_FOUND)


class RegisterViewTest(TestCase):
    url = "/register/"

    def setUp(self):
        self.client = Client()

        self.user = User(username='user', password='user')
        self.user.save()

    def test_get_register_page(self):
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_200_OK)

        # Client authenticated
        self.client.force_login(user=self.user)
        self.assertIn(b'You are already logged in', self.client.get(self.url).content)

    def test_register_new_user(self):
        paswd = 'VeryStrongP@swd481567'
        creation_attrs = {
            'username': 'new',
            'first_name': 'first',
            'last_name': 'last',
            'email': 'email@mail.ru',
            'password1': paswd,
            'password2': paswd,
        }
        self.assertEqual('/', self.client.post(self.url, data=creation_attrs).headers['Location'])

    def test_register_new_user_invalid_attrs(self):
        paswd = 'weakpassword'
        creation_attrs = {
            'username': 'new',
            'first_name': 'first',
            'last_name': 'last',
            'password1': paswd,
            'password2': paswd,
        }
        self.assertIn(b'field is required', self.client.post(self.url, data=creation_attrs).content)


class RecipeViewTest(TestCase):
    url = "/recipes"

    def setUp(self):
        self.client = Client()

        self.user = User(username='user', password='user')
        self.user.save()

        self.client.force_login(user=self.user)
        self.recipe_cat = RecipeCategory.objects.create(id=1, name='Recipe cat 1')
        self.ingredient = Ingredient.objects.create(
            id=1,
            name='Ing1',
            category=IngredientCategory.objects.create(id=1, name='Ing cat 1'),
            price=123,
        )

    def test_get_all(self):
        category_id = self.recipe_cat.id
        self.assertEqual(self.client.get(f"{self.url}/?category_id={category_id}").status_code, status.HTTP_200_OK)

        # Client not authenticated
        self.client.logout()
        self.assertEqual(self.client.get(f"{self.url}/?category_id={category_id}").status_code, status.HTTP_302_FOUND)

    def test_get_one(self):
        created_id = Recipe.objects.create(
            id=123,
            name='Aaaaaa',
            description='abcdefg',
            category=self.recipe_cat,
            user=self.user
        ).id
        instance_url = f'{self.url[:-1]}/?id={created_id}'
        self.assertEqual(self.client.get(instance_url).status_code, status.HTTP_200_OK)

        # Client not authenticated
        self.client.logout()
        self.assertEqual(self.client.get(instance_url).status_code, status.HTTP_302_FOUND)

    def test_get_non_existent(self):
        instance_url = f'{self.url[:-1]}/?id=1356136'
        self.assertIn(b'not found', self.client.get(instance_url).content)

    def test_create_one(self):
        target_url = self.url[:-1] + "/"
        creation_attrs = {
            'name': 'Aaaaaa',
            'description': 'abcdefg',
            'category': self.recipe_cat.id,
            'ingredients': [self.ingredient.id]
        }

        self.assertIn('profile', self.client.post(target_url, data=creation_attrs).headers['Location'])

        # Non existent ingredient
        creation_attrs['ingredients'] = [33141]
        self.assertIn(
            b'not one of the available choices',
            self.client.post(target_url, data=creation_attrs).content,
        )


class IngredientViewTest(TestCase):
    url = "/ingredients"

    def setUp(self):
        self.client = Client()

        self.user = User(username='user', password='user')
        self.user.save()

        self.client.force_login(user=self.user)
        self.ing_cat = IngredientCategory.objects.create(id=1, name='Ing cat 1')

    def test_get_all(self):
        category_id = self.ing_cat.id
        self.assertEqual(self.client.get(f"{self.url}/?category_id={category_id}").status_code, status.HTTP_200_OK)

        # Client not authenticated
        self.client.logout()
        self.assertEqual(self.client.get(f"{self.url}/?category_id={category_id}").status_code, status.HTTP_302_FOUND)

    def test_get_one(self):
        created_id = Ingredient.objects.create(
            id=12,
            name='Aaaaaa',
            category=self.ing_cat,
            price=123,
        ).id
        instance_url = f'{self.url[:-1]}/?id={created_id}'
        self.assertEqual(self.client.get(instance_url).status_code, status.HTTP_200_OK)

        # Client not authenticated
        self.client.logout()
        self.assertEqual(self.client.get(instance_url).status_code, status.HTTP_302_FOUND)

    def test_get_non_existent(self):
        instance_url = f'{self.url[:-1]}/?id=1356136'
        self.assertIn(b'not found', self.client.get(instance_url).content)

    def test_create_one(self):
        target_url = self.url[:-1] + "/"
        creation_attrs = {
            'name': 'Aaaaaa',
            'category': self.ing_cat.id,
            'price': 123
        }

        self.assertEqual(self.client.post(target_url, data=creation_attrs).status_code, status.HTTP_200_OK)

        # Non-existent category
        creation_attrs['category'] = [33141]
        self.assertIn(
            b'not one of the available choices',
            self.client.post(target_url, data=creation_attrs).content,
        )


class RecipeCategoryListViewTest(TestCase):
    url = "/recipe-categories"

    def setUp(self):
        self.client = Client()

        self.user = User(username='user', password='user')
        self.user.save()

        self.client.force_login(user=self.user)

    def test_get_all(self):
        self.assertEqual(self.client.get(self.url + "/").status_code, status.HTTP_200_OK)

        # Client not authenticated
        self.client.logout()
        self.assertEqual(self.client.get(self.url + "/").status_code, status.HTTP_302_FOUND)


class IngredientCategoryListViewTest(TestCase):
    url = "/ingredient-categories"

    def setUp(self):
        self.client = Client()

        self.user = User(username='user', password='user')
        self.user.save()

        self.client.force_login(user=self.user)

    def test_get_all(self):
        self.assertEqual(self.client.get(self.url + "/").status_code, status.HTTP_200_OK)

        # Client not authenticated
        self.client.logout()
        self.assertEqual(self.client.get(self.url + "/").status_code, status.HTTP_302_FOUND)


class CommentViewTest(TestCase):
    url = "/comments"

    def setUp(self):
        self.client = Client()

        self.user = User(username='user', password='user')
        self.user.save()

        self.client.force_login(user=self.user)
        self.recipe_cat = RecipeCategory.objects.create(id=1, name='Recipe cat 1')
        self.recipe = Recipe.objects.create(
            id=156,
            name='Recipe 1',
            description='Just a sample recipe',
            category=RecipeCategory.objects.create(id=5, name='Recipe cat 1'),
            user=self.user
        )

    def test_create_one(self):
        target_url = self.url[:-1] + "/"
        creation_attrs = {
            'text': 'Aaaaaa',
            'recipe': self.recipe.id,
            'user': self.user
        }

        self.assertIn('profile', self.client.post(target_url, data=creation_attrs).headers['Location'])
