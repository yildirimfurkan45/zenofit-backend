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

@api_view(['GET'])
def calculate_calories(request):
    user = get_user_from_request(request)
    if not user:
        return Response({"detail": "Oturum açmanız gerekmektedir."}, status=status.HTTP_401_UNAUTHORIZED)

    weight = user.weight if user.weight else 70.0
    height = user.height if user.height else 170.0
    age = user.age if user.age else 25
    gender = user.gender.lower() if user.gender else 'male'
    activity = user.activity_level.lower() if user.activity_level else 'moderate'
    goal = user.goal.lower() if user.goal else 'maintain'

    if 'female' in gender or 'kadın' in gender:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5

    activity_factors = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very': 1.9
    }
    
    factor = 1.375
    for k, v in activity_factors.items():
        if k in activity:
            factor = v
            break
            
    tdee = bmr * factor

    if 'kilo' in goal or 'lose' in goal or 'zayıf' in goal:
        target_calories = tdee - 500
    elif 'kas' in goal or 'gain' in goal or 'hacim' in goal:
        target_calories = tdee + 300
    else:
        target_calories = tdee

    target_calories = max(1200.0, target_calories)

    height_inches = (height - 152.4) / 2.54
    if 'female' in gender or 'kadın' in gender:
        ideal_w = 45.5 + (2.3 * max(0.0, height_inches))
    else:
        ideal_w = 50.0 + (2.3 * max(0.0, height_inches))

    bmi = weight / ((height / 100) ** 2)

    protein_g = weight * 2.0
    fat_g = (target_calories * 0.25) / 9.0
    carbs_g = (target_calories - (protein_g * 4 + fat_g * 9)) / 4.0

    return Response({
        "total_calories": float(round(target_calories, 1)),
        "meals": {
            "kahvalti": float(round(target_calories * 0.3, 1)),
            "ogle": float(round(target_calories * 0.35, 1)),
            "aksam": float(round(target_calories * 0.25, 1)),
            "ara_ogun": float(round(target_calories * 0.1, 1))
        },
        "bke": float(round(bmi, 1)),
        "ideal_weight": float(round(ideal_w, 1)),
        "protein_need": float(round(protein_g, 1)),
        "carbs_need": float(round(carbs_g, 1)),
        "fat_need": float(round(fat_g, 1))
    }, status=status.HTTP_200_OK)