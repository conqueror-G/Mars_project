from django.db import models

from core.models import TimeStampModel

class User(TimeStampModel):
    name                 = models.CharField(max_length=50, blank=True)
    identity             = models.CharField(max_length=50)
    password             = models.CharField(max_length=200)
    is_location_control  = models.BooleanField(null=True)
    is_equipment_control = models.BooleanField(null=True)

    class Meta:
        db_table = "users"

class History(TimeStampModel):
    user                  = models.ForeignKey("User",on_delete=models.CASCADE)
    repaired_sort         = models.ForeignKey("RepairedSort",on_delete=models.CASCADE)
    repaired_manager      = models.ForeignKey("RepairedManager", on_delete=models.CASCADE)
    equipment_gps_tracker = models.ForeignKey("devices.EquipmentGpsTracker", on_delete=models.CASCADE,null=True)
    equipment             = models.ForeignKey("equipment.Equipment", on_delete=models.CASCADE,null=True)
    repaired_purpose      = models.ForeignKey("RepairedPurpose", on_delete=models.CASCADE,null=True)
    content               = models.CharField(max_length=100, blank=True)
    date                  = models.DateTimeField()
    
    class Meta:
        db_table = "histories"

class Alert(TimeStampModel):
    user                  = models.ForeignKey("User",on_delete=models.CASCADE)
    equipment_gps_tracker = models.ForeignKey("devices.EquipmentGpsTracker", on_delete=models.CASCADE,null=True)
    is_low_battery        = models.BooleanField(default=False)
    is_network_error      = models.BooleanField(default=False)
    
    class Meta:
        db_table = "alert"

class RepairedManager(models.Model):
    repaired_company = models.ForeignKey("RepairedCompany", on_delete= models.CASCADE)
    name             = models.CharField(max_length=100, blank=True)    
    department       = models.CharField(max_length=100, blank=True)  
    phone_number     = models.CharField(max_length=20)
    
    class Meta:
        db_table = "repaired_managers"

class RepairedCompany(models.Model):
    name = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "repaired_companies"

class RepairedPurpose(models.Model):
    content = models.CharField(max_length=100, blank=True)    

    class Meta:
        db_table = "repaired_purposes"

class RepairedSort(models.Model):
    content = models.CharField(max_length=100, blank=True)    

    class Meta:
        db_table = "repaired_sorts"