from recipes.models import IngredientsQuanity, Recipe
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from .models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed')
        model = User

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if request is None:
            return False
        user = request.user
        return (user.is_authenticated and
                Follow.objects.filter(user=user, author=obj).exists())


class IngredientQuanitySerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', read_only=True)
    measurement_unit = serializers.SlugField(
        source='ingredient.measurement_unit', read_only=True)
    name = serializers.SlugField(source='ingredient.name', read_only=True)

    class Meta:
        model = IngredientsQuanity
        fields = ('id', 'name', 'quanity', 'measurement_unit')


class ResipeFollowSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'ingredients', 'name',
            'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        data = obj.recipe.all()
        return IngredientQuanitySerializer(data, many=True).data


class FollowSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')
        model = User

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if request is None:
            return False
        user = request.user
        return (user.is_authenticated and
                Follow.objects.filter(user=user, author=obj).exists())

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_recipes(self, obj):
        user = get_object_or_404(User, email=obj)
        return ResipeFollowSerializer(user.recipes.all(), many=True, context={
                'request': self.context.get('request')
            }).data


class FollowSubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!')
        if Follow.objects.filter(
            user=data['user'], author=data['author']
                ).exists():
            raise serializers.ValidationError('Нельзя подписаться дважды')
        return data

    def to_representation(self, instance):
        return FollowSerializer(instance.author, context={
                'request': self.context.get('request')
            }).data
