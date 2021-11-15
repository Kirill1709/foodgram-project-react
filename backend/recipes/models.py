from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Тег')
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(max_length=150, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=150, verbose_name='Название ингредиента')
    measurement_unit = models.CharField(
        max_length=150, verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes_ingredients',
        max_length=150,
        verbose_name='Ингредиент')
    tags = models.ManyToManyField(
        Tag, related_name='tag_recipes', max_length=150, verbose_name='Тег'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта')
    name = models.CharField(max_length=150, verbose_name='Название рецепта')
    image = models.ImageField(verbose_name='Изображение')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(
            1, message='Значение не может быть меньше 1')])
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
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Ингредиент')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Рецепт')
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Количество ингредиентов'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_in_recipe')
        ]


class Favourite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorite',
        on_delete=models.CASCADE,
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite',
        on_delete=models.CASCADE,
        verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite')
        ]


class ShopingCart(models.Model):
    user = models.ForeignKey(
        User,
        related_name='shoping_cart',
        on_delete=models.CASCADE,
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_shoping_cart',
        on_delete=models.CASCADE,
        verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_shoping_cart')
        ]
