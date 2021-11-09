from rest_framework import serializers

from recipes.models import Recipe

from .models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed')
        model = User

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if (user.is_authenticated and
                Follow.objects.filter(user=user, author=obj).exists()):
            return True
        return False


class FollowSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')
        model = User

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if (user.is_authenticated and
                Follow.objects.filter(user=user, author=obj).exists()):
            return True
        return False

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_recipes(self, obj):
        from recipes.serializers import ResipeFollowSerializer
        user = User.objects.get(email=obj)
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
