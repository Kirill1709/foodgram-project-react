from rest_framework import permissions, status
from rest_framework.generics import (ListAPIView, RetrieveAPIView,
                                     get_object_or_404)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Follow, User
from .serializers import (FollowSerializer, FollowSubscribeSerializer,
                          UserSerializer)


class UserView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def get_object(self):
        return get_object_or_404(User, pk=self.kwargs.get('pk'))


class FollowView(ListAPIView):
    serializer_class = FollowSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class FollowSubscribeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        user = self.request.user
        data = {
            'user': user.id,
            'author': pk
        }
        serializer = FollowSubscribeSerializer(
            data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        follow = get_object_or_404(Follow, user=request.user.id, author=pk)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
