from django.db import models

# Create your models here.

class Price(models.Model):
    initial_price = models.FloatField(blank = False, null= False)
    anchor = models.IntegerField(blank = False, null= False)
    extra_price = models.FloatField(blank = False, null= False)
    price_percent = models.FloatField(blank = False, null= False)
    price_protect = models.FloatField(blank = False, null= False)
    class Meta:
        db_table = 'Price'

    def __str__(self):
        return str(self.initial_price)
