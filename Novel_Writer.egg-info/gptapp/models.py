from django.db import models

from django.contrib.auth.models import User

class ApiKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    usage = models.CharField(max_length=255)
    def __str__(self):
        return self.key

class NovelProject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    outline = models.IntegerField(default=0)
    chapter = models.IntegerField(default=0)