from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(max_length=150, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(max_length=150)
    measurement_unit = models.CharField(max_length=150)

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredients, related_name='ingredients', max_length=150)
    tags = models.ManyToManyField(
        Tag, related_name='tags', max_length=150
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to='media/')
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)])
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class IngredientsQuanity(models.Model):
    ingredient = models.ForeignKey(
        Ingredients, on_delete=models.CASCADE,
        related_name='recipe_ingredient')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe')
    quanity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)])


class Favourites(models.Model):
    user = models.ForeignKey(
        User, related_name='favorite', on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe, related_name='farotite', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite')
        ]


class ShopingCart(models.Model):
    user = models.ForeignKey(
        User, related_name='shoping_cart', on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe, related_name='in_shoping_cart', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_shoping_cart')
        ]
