import datetime

from django.db import models

from core.models import TimeStampModel

class MainCategory(models.Model):
    name = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = "maincategories"

class Category(models.Model):
    name          = models.CharField(max_length=50, blank=True)
    main_category = models.ForeignKey("MainCategory", on_delete=models.CASCADE,default='')

    class Meta:
        db_table = "categories"

class EquipmentGpsTracker(TimeStampModel):
    main_category    = models.ForeignKey("MainCategory", on_delete= models.CASCADE)
    company          = models.ForeignKey("equipment.Company", on_delete= models.CASCADE)
    qr_code          = models.CharField(max_length=100,null=True)
    is_power         = models.BooleanField(default=True)
    is_matched       = models.BooleanField(default=False)
    serial_number    = models.CharField(max_length=100)

    class Meta:
        db_table = "equipment_gps_trackers"

class EquipmentGpsTrackerRealtime(TimeStampModel):
    equipment_gps_tracker = models.ForeignKey("EquipmentGpsTracker", on_delete= models.CASCADE)
    error                 = models.ForeignKey("Error", on_delete= models.CASCADE,null=True)
    status                = models.ForeignKey("Status", on_delete= models.CASCADE,null=True)
    latitude              = models.DecimalField(max_digits=20, decimal_places=14, default=0.0)
    longitude             = models.DecimalField(max_digits=20, decimal_places=14, default=0.0)
    statellites_used      = models.IntegerField(null=True)
    battery               = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    class Meta:
        db_table = "equipment_gps_tracker_realtime"

class EquipmentDevice(TimeStampModel):
    user                  = models.ForeignKey('users.User', on_delete=models.CASCADE)
    equipment             = models.ForeignKey('equipment.Equipment', on_delete=models.CASCADE)
    equipment_gps_tracker = models.ForeignKey('EquipmentGpsTracker', on_delete=models.CASCADE)
    is_matched            = models.BooleanField(default=False,null=True)
    
    class Meta:
        db_table = "equipment_devices"

class Status(models.Model):
    content = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = "status"

class Error(models.Model):
    content = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "errors"