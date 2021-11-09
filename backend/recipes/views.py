from rest_framework import mixins, permissions, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (Favourites, Ingredients, IngredientsQuanity,
                     Recipe, ShopingCart, Tag)
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (FavoriteRecipeSerializer, IngredientSerizalizer,
                          RecipeCreateSerializer, ShopingCartSerializer,
                          TagSerializer)
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from rest_framework.decorators import api_view, permission_classes
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_cart(request):
    buf = io.BytesIO()
    pdfmetrics.registerFont(TTFont('Times', 'times.ttf', 'UTF-8'))
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Times", 14)
    ingredient_list = {}
    ingredients = IngredientsQuanity.objects.filter(
        recipe__in_shoping_cart__user=request.user.id)
    for ingredient in ingredients:
        name = ingredient.ingredient.name
        if name in ingredient_list:
            ingredient_list[name]['quanity'] += ingredient.quanity
        else:
            value = {
                'name': name,
                'measurement_unit': ingredient.ingredient.measurement_unit,
                'quanity': ingredient.quanity
            }
            ingredient_list[f'{name}'] = value
    textob.textLine("Количество продуктов для покупки:")
    textob.textLine("")
    for line in ingredient_list:
        name = ingredient_list[f'{line}']['name']
        quanity = ingredient_list[f'{line}']['quanity']
        measurement_unit = ingredient_list[f'{line}']['measurement_unit']
        textob.textLine(f"-  {name} ({measurement_unit})   —   {quanity} ")
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename='shop_cart.pdf')


class ListDetailViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    pass


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)


class IngredientsViewSet(ListDetailViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerizalizer


class TagsViewSet(ListDetailViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class FavoriteRecipeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        user = self.request.user
        data = {
            'user': user.id,
            'recipe': pk
        }
        serializer = FavoriteRecipeSerializer(
            data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        favorite = get_object_or_404(
            Favourites, user=request.user.id, recipe=pk)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShopingCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        user = self.request.user
        data = {
            'user': user.id,
            'recipe': pk
        }
        serializer = ShopingCartSerializer(
            data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        recipe = get_object_or_404(
            ShopingCart, user=request.user.id, recipe=pk)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
