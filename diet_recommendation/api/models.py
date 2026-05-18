from django.db import models

class Recipe(models.Model):
    name = models.CharField(max_length=255)
    calories = models.FloatField()
    protein_content = models.FloatField()
    carbohydrate_content = models.FloatField()
    fat_content = models.FloatField()
    # Diğer alanlar...

    def __str__(self):
        return self.name

class AppUser(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    goal = models.CharField(max_length=100, null=True, blank=True)
    activity_level = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.email