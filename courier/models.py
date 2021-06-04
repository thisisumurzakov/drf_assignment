from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Courier(models.Model):
    type_choice = (
        ('foot', 'foot'),
        ('bike', ' bike'),
        ('car', 'car'),
    )
    courier_type = models.CharField(max_length=4, choices=type_choice)
    regions = ArrayField(models.IntegerField())
    working_hours = ArrayField(models.CharField(max_length=11), null=True, blank=True)

class Order(models.Model):
    courier_field = models.ForeignKey(Courier, on_delete=models.CASCADE, null=True, blank=True)
    weight = models.FloatField(validators=[MinValueValidator(0.01), MaxValueValidator(50)],)
    region = models.SmallIntegerField()
    delivery_hours = ArrayField(models.CharField(max_length=11))
    assign_time = models.DateTimeField(default=None, null=True, blank=True)
    complete_time = models.DateTimeField(default=None, null=True, blank=True)
    time = models.IntegerField(null=True, blank=True)