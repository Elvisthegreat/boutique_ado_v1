from django.db import models

# Create your models here.
class Category(models.Model):

    """We can fix the spelling issue on the category model with meta class
       by adding a special metaclass to the model itself because
       django added 's' to the Categorys like this."""
    class Meta:
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)


    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Product(models.Model):
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL) # if a Category is deleted SET_NULL instead of deleting it
    sku = models.CharField(max_length=254, null=True, blank=True) # sku stands for Stock Keeping Unit
    name = models.CharField(max_length=254)
    description = models.TextField()
    has_sizes = models.BooleanField(default=False, null=True, blank=True) # for clothes sizing
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name
