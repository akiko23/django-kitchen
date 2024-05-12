from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from kitchen_app.models import Recipe, Ingredient, Comment, RecipeCategory, IngredientCategory


class RecipeAPITest(TestCase):
    url = "/api/recipes/"

    def setUp(self):
        self.client = APIClient()

        self.user = User(username='user', password='user')
        self.user.save()
        self.superuser = User(username='admin', password='admin', is_superuser=True)
        self.superuser.save()

        self.user_token = Token(user=self.user)
        self.superuser_token = Token(user=self.superuser)

        self.r_cat = RecipeCategory.objects.create(id=1, name='1')
        
        i_cat = IngredientCategory.objects.create(id=1, name='a')
        self.ingredient = Ingredient.objects.create(id=1, name='a', category=i_cat, price=2)

    def api_methods(
            self, user: User, token: Token,
            post_exp: int, put_exp: int, delete_exp: int,
    ):
        self.client.force_authenticate(user=user, token=token)

        creation_attrs =  {'name': 'Aaaaaa', 'description': 'abcdefg'}

        self.created_id = Recipe.objects.create(**creation_attrs, category=self.r_cat, user=user).id
        instance_url = f'{self.url}{self.created_id}/'

        creation_attrs['category'] = self.r_cat.id
        creation_attrs['ingredients'] = [{"ingredient_id": self.ingredient.id, "quantity": 2}]
        # GET all
        self.assertEqual(self.client.options(self.url).status_code, status.HTTP_200_OK)

        # HEAD all
        self.assertEqual(self.client.head(self.url).status_code, status.HTTP_200_OK)

        # OPTIONS all
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_200_OK)

        # GET instance
        self.assertEqual(self.client.get(instance_url).status_code, status.HTTP_200_OK)

        # OPTIONS instance
        self.assertEqual(self.client.get(instance_url).status_code, status.HTTP_200_OK)

        # POST
        self.assertEqual(self.client.post(self.url, creation_attrs, format='json').status_code, post_exp)

        # PUT
        self.assertEqual(self.client.put(instance_url, creation_attrs, format='json').status_code, put_exp)

        # DELETE
        self.assertEqual(self.client.delete(instance_url).status_code, delete_exp)

    def test_superuser(self):
        self.api_methods(
            self.superuser, self.superuser_token,
            status.HTTP_201_CREATED, status.HTTP_200_OK, status.HTTP_204_NO_CONTENT
        )

    def test_user(self):
        self.api_methods(
            self.user, self.user_token,
            status.HTTP_201_CREATED, status.HTTP_200_OK, status.HTTP_204_NO_CONTENT
        )


class IngredientAPITest(TestCase):
    url = "/api/ingredients/"

    def setUp(self):
        self.client = APIClient()

        self.user = User(username='user', password='user')
        self.user.save()
        self.superuser = User(username='admin', password='admin', is_superuser=True)
        self.superuser.save()

        self.user_token = Token(user=self.user)
        self.superuser_token = Token(user=self.superuser)

        self.i_cat = IngredientCategory.objects.create(id=1, name='a')

    def api_methods(
            self, user: User, token: Token,
            post_exp: int, put_exp: int, delete_exp: int,
    ):
        self.client.force_authenticate(user=user, token=token)

        creation_attrs =  {'name': 'Z', 'price': 2}

        self.created_id = Ingredient.objects.create(**creation_attrs, category=self.i_cat).id
        instance_url = f'{self.url}{self.created_id}/'

        creation_attrs['category'] = self.i_cat.id
        # GET all
        self.assertEqual(self.client.options(self.url).status_code, status.HTTP_200_OK)

        # HEAD all
        self.assertEqual(self.client.head(self.url).status_code, status.HTTP_200_OK)

        # OPTIONS all
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_200_OK)

        # GET instance
        self.assertEqual(self.client.get(instance_url).status_code, status.HTTP_200_OK)

        # OPTIONS instance
        self.assertEqual(self.client.get(instance_url).status_code, status.HTTP_200_OK)

        # POST
        creation_attrs['name'] = 'fasf'
        self.assertEqual(self.client.post(self.url, creation_attrs, format='json').status_code, post_exp)

        # PUT
        creation_attrs['name'] = 'fasf2'
        self.assertEqual(self.client.put(instance_url, creation_attrs, format='json').status_code, put_exp)

        # DELETE
        self.assertEqual(self.client.delete(instance_url).status_code, delete_exp)

    def test_superuser(self):
        self.api_methods(
            self.superuser, self.superuser_token,
            status.HTTP_201_CREATED, status.HTTP_200_OK, status.HTTP_204_NO_CONTENT
        )

    def test_user(self):
        self.api_methods(
            self.user, self.user_token,
            status.HTTP_403_FORBIDDEN, status.HTTP_403_FORBIDDEN, status.HTTP_403_FORBIDDEN
        )


class CommentAPITest(TestCase):
    url = "/api/comments/"

    def setUp(self):
        self.client = APIClient()

        self.user = User(username='user', password='user')
        self.user.save()
        self.superuser = User(username='admin', password='admin', is_superuser=True)
        self.superuser.save()

        self.user_token = Token(user=self.user)
        self.superuser_token = Token(user=self.superuser)

        i_cat = IngredientCategory.objects.create(id=1, name='a')
        ingredient = Ingredient.objects.create(id=1, name='a', category=i_cat, price=2)

        r_cat = RecipeCategory.objects.create(id=1, name='1')
        self.recipe = Recipe.objects.create(name='A', description='afasfafssa', category=r_cat, user=self.superuser)
        self.recipe.ingredients.set([ingredient])

    def api_methods(
            self, user: User, token: Token,
            post_exp: int, put_exp: int, delete_exp: int,
    ):
        self.client.force_authenticate(user=user, token=token)

        creation_attrs =  {'text': 'bla bla'}

        self.created_id = Comment.objects.create(**creation_attrs, user=self.user, recipe=self.recipe).id
        instance_url = f'{self.url}{self.created_id}/'

        creation_attrs['recipe_id'] = self.recipe.id
        creation_attrs['user_id'] = user.id

        # GET all
        self.assertEqual(self.client.options(self.url).status_code, status.HTTP_200_OK)

        # HEAD all
        self.assertEqual(self.client.head(self.url).status_code, status.HTTP_200_OK)

        # OPTIONS all
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_200_OK)

        # GET instance
        self.assertEqual(self.client.get(instance_url).status_code, status.HTTP_200_OK)

        # OPTIONS instance
        self.assertEqual(self.client.get(instance_url).status_code, status.HTTP_200_OK)

        # POST
        self.assertEqual(self.client.post(self.url, creation_attrs, format='json').status_code, post_exp)

        # PUT
        self.assertEqual(self.client.put(instance_url, creation_attrs, format='json').status_code, put_exp)

        # DELETE
        self.assertEqual(self.client.delete(instance_url).status_code, delete_exp)

    def test_superuser(self):
        self.api_methods(
            self.superuser, self.superuser_token,
            status.HTTP_201_CREATED, status.HTTP_200_OK, status.HTTP_204_NO_CONTENT
        )

    def test_user(self):
        self.api_methods(
            self.user, self.user_token,
            status.HTTP_201_CREATED, status.HTTP_200_OK, status.HTTP_204_NO_CONTENT
        )
