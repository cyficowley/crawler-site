from django.db import models
# Create your models here.


class sites(models.Model):
    url = models.CharField(max_length=1000)
    list = models.CharField(max_length=1000)

    def __str__(self):
        return self.url

    class Meta:
        verbose_name_plural = "sites"


class statuses(models.Model):
    url = models.CharField(max_length=1000)
    code = models.CharField(max_length=1000)

    def __str__(self):
        return self.url

    class Meta:
        verbose_name_plural = "statuses"


class redirects(models.Model):
    old_url = models.CharField(max_length=1000)
    new_url = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.old_url) + " to " + str(self.new_url)

    class Meta:
        verbose_name_plural = "redirects"