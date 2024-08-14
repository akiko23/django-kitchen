from rest_framework import serializers

from .models import (
    Comment,
    Ingredient,
    IngredientCategory,
    Recipe,
    RecipeCategory,
    RecipeIngredient,
)


class IngredientCategorySerializer(serializers.HyperlinkedModelSerializer):
    def __repr__(self):  # pragma: no cover
        return "ingredient-categories"

    class Meta:
        model = IngredientCategory
        fields = [
            'id', 'name'
        ]


class IngredientSerializer(serializers.HyperlinkedModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=IngredientCategory.objects.all(),
        many=False)

    class Meta:
        model = Ingredient
        fields = [
            'id', 'name', 'price', 'category'
        ]


class RecipeIngredientSerializer(serializers.HyperlinkedModelSerializer):
    ingredient_id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        many=False, write_only=True)
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    quantity = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = [
            'quantity', 'ingredient_id', 'id'
        ]


class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=RecipeCategory.objects.all(),
        many=False)

    ingredients = RecipeIngredientSerializer(many=True, allow_null=True)

    def update(self, instance: Recipe, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.category = validated_data.get('category', instance.category)

        instance.save()
        return instance

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'description', 'user_id',
            'created_at', 'category', 'ingredients'
        ]


class RecipeCategorySerializer(serializers.HyperlinkedModelSerializer):
    def __repr__(self):  # pragma: no cover
        return "recipe-categories"

    class Meta:
        model = RecipeCategory
        fields = [
            'id', 'name'
        ]


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    recipe_id = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        many=False)

    class Meta:
        model = Comment
        fields = [
            'id', 'text', 'user_id',
            'published_on', 'recipe_id'
        ]
