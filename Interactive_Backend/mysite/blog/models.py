from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.EmailField()
    essay=models.TextField(default='null')

class UserClass(models.Model):
    userId = models.TextField(primary_key=True)
    user_Recommand = models.TextField()
    user_History = models.TextField()

class MovieClass(models.Model):
    movieId = models.TextField(primary_key=True)
    movie_info = models.TextField(max_length=1000)
    movie_src = models.TextField()