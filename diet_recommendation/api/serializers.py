from rest_framework import serializers
from .models import Recipe, AppUser

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'

class AppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user_id'] = data.pop('id')
        if 'created_at' in data and data['created_at']:
            data['created_at'] = str(data['created_at'])
        return data