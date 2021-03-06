from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from users.serializers import UserSerializer

from .models import (Favourite, Ingredient, IngredientsQuanity, Recipe,
                     ShopingCart, Tag)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerizalizer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class AddIngredientQuanitySerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', read_only=True)
    measurement_unit = serializers.SlugField(
        source='ingredient.measurement_unit', read_only=True)
    name = serializers.SlugField(source='ingredient.name', read_only=True)

    class Meta:
        model = IngredientsQuanity
        fields = ('id', 'name', 'amount', 'measurement_unit')


class IngredientQuanitySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsQuanity
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'is_favorited', 'is_in_shopping_cart',
            'ingredients', 'name', 'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        data = obj.recipe.all()
        return AddIngredientQuanitySerializer(data, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None:
            return False
        user = request.user
        return (user.is_authenticated
                and Favourite.objects.filter(user=user, recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None:
            return False
        user = request.user
        return (user.is_authenticated
                and ShopingCart.objects.filter(user=user, recipe=obj).exists())

    def get_image(self, obj):
        return obj.image.url


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientQuanitySerializer(many=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text',
            'cooking_time'
        ]

    def create(self, validated_data):
        user = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=user, **validated_data)
        self.create_ingredients_tags_list(ingredients, recipe, tags)
        recipe.save()
        return recipe

    def to_representation(self, instance):
        return RecipeSerializer(instance, context={
            'request': self.context.get('request')
        }).data

    def update(self, instance, validated_data):
        recipe = get_object_or_404(Recipe, pk=instance.id)
        recipe.tags.clear()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        IngredientsQuanity.objects.filter(recipe=recipe).delete()
        self.create_ingredients_tags_list(ingredients, recipe, tags)
        recipe.image.delete()
        return super().update(instance, validated_data)

    def validate(self, data):
        ingredients = data['ingredients']
        tags = data['tags']
        ingredient_id = []
        for ingredient in ingredients:
            ingredient_id.append(ingredient['id'])
            if ingredient['amount'] < 0:
                raise serializers.ValidationError(
                    '???????????????????? ?????????????????????? ???????????? ???????? ???????????? ????????')
        if len(ingredient_id) != len(set(ingredient_id)):
            raise serializers.ValidationError(
                '???????????????????? ???????????? ???????? ???????????????????? ?? ??????????????')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                '?????? ???????????? ???????? ???????????????????? ?? ??????????????')
        return data

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                '?????????? ?????????????????????????? ???????????? ???????? ???????????? 1')
        return value

    def create_ingredients_tags_list(self, ingredients, recipe, tags):
        for ingredient in ingredients:
            id_ingredient = ingredient.get('id')
            amount = ingredient.get('amount')
            ingredient_id = get_object_or_404(Ingredient, pk=id_ingredient)
            IngredientsQuanity.objects.create(
                recipe=recipe, ingredient=ingredient_id, amount=amount)
        for tag in tags:
            recipe.tags.add(tag)


class FavoriteShowSerializer(RecipeSerializer):

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'image', 'cooking_time'
        ]


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favourite
        fields = ('user', 'recipe')

    def validate(self, data):
        if Favourite.objects.filter(
            user=data['user'], recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                '???????????? ?????? ?????????????????? ?? ??????????????????')
        return data

    def to_representation(self, instance):
        return FavoriteShowSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data


class ShopingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        if ShopingCart.objects.filter(
            user=data['user'], recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                '???????????? ?????? ?????????????????? ?? ???????????? ??????????????')
        return data

    def to_representation(self, instance):
        return FavoriteShowSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data
