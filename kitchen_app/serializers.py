from rest_framework import serializers
from .models import Recipe, Ingredient

class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'description', 
            'category', 'ingredients', 'created_at',
        ]

class IngredientSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ingredient
        fields = [
            'id', 'name', 'category', 'price',
        ]
