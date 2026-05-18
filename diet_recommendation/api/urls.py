from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, login_user, register_user, user_me, get_user_by_id, calculate_calories

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', login_user, name='login_user'),
    path('users/', register_user, name='register_user'),
    path('users/me', user_me, name='user_me'),
    path('users/me/', user_me, name='user_me_slash'),
    path('users/<int:pk>/', get_user_by_id, name='get_user_by_id'),
    path('nutrition/ai/calculate-calories', calculate_calories, name='calculate_calories'),
    path('nutrition/ai/calculate-calories/', calculate_calories, name='calculate_calories_slash'),
]