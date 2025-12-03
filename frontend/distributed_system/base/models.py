from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='avatars/default.jpg', upload_to='avatars/', blank=True, null=True)
    pay = models.CharField(max_length=50, default='0')  # default value
    ville = models.CharField(max_length=50, default='Unknown')  # default value

    def __str__(self):
        return f'{self.user.username} Profile'


class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="history_images/")
    result = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']