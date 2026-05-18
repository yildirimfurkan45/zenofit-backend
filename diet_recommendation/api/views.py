import pandas as pd
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework import status
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from .models import Recipe, AppUser
from .serializers import RecipeSerializer, AppUserSerializer

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

# Helper for token extraction
def get_user_from_request(request):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            user_id = int(token.split("_")[1])
            return AppUser.objects.get(id=user_id)
        except Exception:
            return None
    return None

@api_view(['POST'])
def register_user(request):
    email = request.data.get('email')
    password = request.data.get('password')
    name = request.data.get('name', '')

    if not email or not password:
        return Response({"detail": "Email ve şifre gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

    if AppUser.objects.filter(email=email).exists():
        return Response({"detail": "Bu email adresi zaten kullanımda."}, status=status.HTTP_400_BAD_REQUEST)

    user = AppUser.objects.create(email=email, password=password, name=name)
    serializer = AppUserSerializer(user)
    
    return Response({
        "access_token": f"token_{user.id}",
        "token_type": "bearer",
        "user": serializer.data
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({"detail": "Email ve şifre gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = AppUser.objects.get(email=email, password=password)
    except AppUser.DoesNotExist:
        return Response({"detail": "E-posta adresi veya şifre hatalı."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = AppUserSerializer(user)
    return Response({
        "access_token": f"token_{user.id}",
        "token_type": "bearer",
        "user": serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['GET', 'PUT'])
def user_me(request):
    user = get_user_from_request(request)
    if not user:
        return Response({"detail": "Oturum açmanız gerekmektedir."}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        serializer = AppUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = AppUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_user_by_id(request, pk):
    try:
        user = AppUser.objects.get(id=pk)
    except AppUser.DoesNotExist:
        return Response({"detail": "Kullanıcı bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

    serializer = AppUserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)