import io

import reportlab
from django.conf import settings
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import IngredientFilter, RecipeFilter
from .mixins import ListDetailViewSet
from .models import (Favourite, Ingredient, IngredientsQuanity, Recipe,
                     ShopingCart, Tag)
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (FavoriteRecipeSerializer, IngredientSerizalizer,
                          RecipeCreateSerializer, ShopingCartSerializer,
                          TagSerializer)
from .paginators import PageNumberPaginatorCustom


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_cart(request):
    reportlab.rl_config.TTFSearchPath.append(str(settings.BASE_DIR))
    buf = io.BytesIO()
    pdfmetrics.registerFont(TTFont('Times', 'times.ttf', 'UTF-8'))
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Times", 14)
    ingredient_list = {}
    ingredients = IngredientsQuanity.objects.filter(
        recipe__in_shoping_cart__user=request.user.id).values_list(
            'ingredient_id', 'amount')
    for ingredient in ingredients:
        ingredient_object = get_object_or_404(Ingredient, id=ingredient[0])
        name = ingredient_object.name
        if name in ingredient_list:
            ingredient_list[name]['amount'] += ingredient[1]
        else:
            value = {
                'name': name,
                'measurement_unit': ingredient_object.measurement_unit,
                'amount': ingredient[1]
            }
            ingredient_list[f'{name}'] = value
    textob.textLine("Количество продуктов для покупки:")
    textob.textLine("")
    for line in ingredient_list:
        name = ingredient_list[f'{line}']['name']
        quanity = ingredient_list[f'{line}']['amount']
        measurement_unit = ingredient_list[f'{line}']['measurement_unit']
        textob.textLine(f"-  {name} ({measurement_unit})   —   {quanity} ")
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename='shop_cart.pdf')


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    pagination_class = PageNumberPaginatorCustom


class IngredientsViewSet(ListDetailViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerizalizer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filter_class = IngredientFilter


class TagsViewSet(ListDetailViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [permissions.AllowAny, ]


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
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        favorite = get_object_or_404(
            Favourite, user=request.user.id, recipe=pk)
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
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        recipe = get_object_or_404(
            ShopingCart, user=request.user.id, recipe=pk)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
