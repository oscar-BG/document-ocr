from django.db import models

# Create your models here.
class Person(models.Model):
    card_id             = models.CharField(max_length=50)
    name                = models.CharField(max_length=255)
    last_name           = models.CharField(max_length=255)
    second_last_name    = models.CharField(max_length=255)


class SubirDumentoImagen(models.Model):
    documento = models.FileField(upload_to='documents/')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        db_table = "¨files"
        ordering = ['-created_at']