from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone_number = models.CharField(max_length=15, blank=True)
    photo_url = models.CharField(max_length=100, blank=True)
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=15, blank=True)
    description = models.CharField(max_length=300, blank=True)
    price = models.IntegerField(blank=True, default=0)

    def update(self, new_fields):
        if self.name != new_fields['name']:
            self.name = new_fields['name']
        if self.description != new_fields['description']:
            self.description = new_fields['description']
        if self.price != new_fields['price']:
            self.price = new_fields['price']
        self.save()


class Photo(models.Model):
    url = models.CharField(max_length=150)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
