from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from users.serializers import UserSerializer

from .models import (Favourites, Ingredients, IngredientsQuanity,
                     Recipe, ShopingCart, Tag)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerizalizer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = '__all__'


class AddIngredientQuanitySerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', read_only=True)
    measurement_unit = serializers.SlugField(
        source='ingredient.measurement_unit', read_only=True)
    name = serializers.SlugField(source='ingredient.name', read_only=True)

    class Meta:
        model = IngredientsQuanity
        fields = ('id', 'name', 'quanity', 'measurement_unit')


class IngredientQuanitySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    quanity = serializers.IntegerField()

    class Meta:
        model = IngredientsQuanity
        fields = ('id', 'quanity')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'is_favorited', 'is_in_shopping_cart',
            'ingredients', 'name', 'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        data = obj.recipe.all()
        return AddIngredientQuanitySerializer(data, many=True).data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if (user.is_authenticated and
                Favourites.objects.filter(user=user, recipe=obj).exists()):
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if (user.is_authenticated and
                ShopingCart.objects.filter(user=user, recipe=obj).exists()):
            return True
        return False


class ResipeFollowSerializer(RecipeSerializer):

    class Meta:
        model = Recipe
        fields = (
                'id', 'tags', 'ingredients',
                'name', 'image', 'text', 'cooking_time')


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
        [recipe.tags.add(tag) for tag in tags]
        for ingredient in ingredients:
            id_ingredient = ingredient.get('id')
            quanity = ingredient.get('quanity')
            ingredient_id = get_object_or_404(Ingredients, pk=id_ingredient)
            IngredientsQuanity.objects.create(
                recipe=recipe, ingredient=ingredient_id, quanity=quanity)
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
        for ingredient in ingredients:
            id_ingredient = ingredient.get('id')
            quanity = ingredient.get('quanity')
            ingredient_id = get_object_or_404(Ingredients, pk=id_ingredient)
            IngredientsQuanity.objects.create(
                recipe=recipe, ingredient=ingredient_id, quanity=quanity)
        recipe.image.delete()
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        [recipe.tags.add(tag) for tag in tags]
        instance.save()
        return instance


class FavoriteShowSerializer(RecipeSerializer):

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'image', 'cooking_time'
        ]


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favourites
        fields = ('user', 'recipe')

    def validate(self, data):
        if Favourites.objects.filter(
            user=data['user'], recipe=data['recipe']
                ).exists():
            raise serializers.ValidationError(
                'Рецепт уже находится в избранном')
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
                'Рецепт уже находится в списке покупок')
        return data

    def to_representation(self, instance):
        return FavoriteShowSerializer(instance.recipe, context={
                'request': self.context.get('request')
            }).data
