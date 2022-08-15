from django.db import models

from core.models import TimeStampModel

class Equipment(TimeStampModel):
    main_category                    = models.ForeignKey("devices.MainCategory", on_delete=models.CASCADE)
    company                          = models.ForeignKey("Company", on_delete=models.CASCADE)
    unit                             = models.ForeignKey("Unit", on_delete= models.CASCADE)
    equipment_category               = models.ForeignKey("EquipmentCategory", on_delete=models.CASCADE)
    equipment_type                   = models.ForeignKey("EquipmentType", on_delete=models.CASCADE)
    capacity                         = models.IntegerField(null=True)
    plate_number                     = models.CharField(max_length=100)
    manufacture_date                 = models.DateTimeField()
    qr_code                          = models.CharField(max_length=100,null=True)
    is_power                         = models.BooleanField(default=True)
    original_id                      = models.CharField(max_length=100,unique=True)
    maintenance_company              = models.CharField(max_length=50, blank=True)
    maintenance_manager_name         = models.CharField(max_length=50, blank=True)
    maintenance_manager_phone_number = models.CharField(max_length=50,default='')
    maintenance_manager_department   = models.CharField(max_length=50, blank=True)
    driver                           = models.ForeignKey("Driver", on_delete= models.CASCADE,null=True)

    class Meta:
        db_table = "equipments"

class EquipmentCategory(models.Model):
    name      = models.CharField(max_length=50, blank=True)
    image_url = models.URLField()

    class Meta:
        db_table = "equipment_categories"

class EquipmentType(models.Model):
    name = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = "equipment_types"

class Unit(models.Model):
    name = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = "units"

class Driver(models.Model):
    name           = models.CharField(max_length=50, blank=True)
    level          = models.ForeignKey("Level", on_delete=models.CASCADE)
    driver_company = models.ForeignKey("DriverCompany", on_delete=models.CASCADE)

    class Meta:
        db_table = "drivers"

class DriverCompany(models.Model):
    name = models.CharField(max_length=70, blank=True)

    class Meta:
        db_table = "driver_companies"

class Level(models.Model):
    name = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "levels"

class Company(models.Model):
    name = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = "companies"


