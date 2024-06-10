from django.db import models
from django.core.validators import MinValueValidator

from django.conf.global_settings import AUTH_USER_MODEL


class RecipeCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, null=False)

    def __repr__(self):
        return str(self.id)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "recipe_categories"
        verbose_name = 'recipe category'
        verbose_name_plural = 'recipe categories'


class IngredientCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, null=False)

    def __repr__(self):
        return str(self.id)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "ingredient_categories"
        verbose_name = 'ingredient category'
        verbose_name_plural = 'ingredient categories'


class Recipe(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, null=False)
    description = models.TextField(null=False)
    
    category = models.ForeignKey("RecipeCategory", null=True, on_delete=models.DO_NOTHING)
    ingredients = models.ManyToManyField("Ingredient", through="RecipeIngredient")
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name} by {self.user}"
    
    class Meta:
        db_table = "recipes"
        verbose_name = 'recipe'
        verbose_name_plural = 'recipes'


class Ingredient(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, null=False, unique=True)
    category = models.ForeignKey("IngredientCategory", on_delete=models.CASCADE)
    price = models.IntegerField(
        null=False, 
        blank=False,
        validators=[
            MinValueValidator(1),
        ],
        help_text="price per 100g in rubles"
    )

    def __str__(self) -> str:
        return self.name 

    
    class Meta:
        db_table = "ingredients"
        verbose_name = 'ingredient'
        verbose_name_plural = 'ingredients'


class RecipeIngredient(models.Model):
    quantity = models.IntegerField(
        null=False, 
        blank=False, 
        default=1,
        validators=[
            MinValueValidator(1),
        ],
    )
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE)
    ingredient = models.ForeignKey("Ingredient", on_delete=models.CASCADE)


    def __str__(self) -> str:
        return f"{self.ingredient.name} for {self.recipe.name}" 
    
    class Meta:
        db_table = "recipes_ingredients"
        unique_together = (
            ("recipe", "ingredient")
        )
        verbose_name = 'relationship between recipe and ingredient'
        verbose_name_plural = 'relationships between recipes and ingredients'



class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField(null=False)
    published_on = models.DateTimeField(null=False, auto_now=True)
    
    recipe = models.ForeignKey(to="Recipe", on_delete=models.DO_NOTHING)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.DO_NOTHING)

    def __str__(self) -> str:
        return f"Comment {self.id} to {self.recipe.name}"

    class Meta:
        db_table = "comments"
        verbose_name = 'comment'
        verbose_name_plural = 'comments'
