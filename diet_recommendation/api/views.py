import pandas as pd
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from .models import Recipe
from .serializers import RecipeSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    @action(detail=False, methods=['post'])
    def recommend(self, request):
        calorie_limit = request.data.get('calorie_limit', 2000)
        recipes = Recipe.objects.all().values()
        df = pd.DataFrame(recipes)
        # Yapay zeka fonksiyonlarını burada kullanın
        # Örnek:
        # recommendations = create_diet_list(df, calorie_limit)
        # return Response(recommendations.to_dict(orient='records'))