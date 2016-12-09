from django.db import models

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return "%s %s" % (self.name, self.email)


class Meme(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    score = models.IntegerField()
    url = models.CharField(max_length=60)

    def __str__(self):
        return "%s %s %s" % (self.name, self.url, self.score)