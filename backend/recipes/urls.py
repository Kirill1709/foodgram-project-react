from django.urls import include, path
from rest_framework import routers

from .views import (FavoriteRecipeView, IngredientsViewSet, RecipeViewSet,
                    ShopingCartView, TagsViewSet, download_cart)

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')
router.register(r'tags', TagsViewSet, basename='tags')


urlpatterns = [
    path('recipes/download_shopping_cart/', download_cart,
         name='download_cart'),
    path('recipes/<int:pk>/shopping_cart/', ShopingCartView.as_view(),
         name='shopping_cart'),
    path('recipes/<int:pk>/favorite/', FavoriteRecipeView.as_view(),
         name='favorite'),
    path('', include(router.urls)),
]
