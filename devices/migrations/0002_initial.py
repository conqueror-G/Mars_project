# Generated by Django 4.0.6 on 2022-07-26 11:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('equipment', '0001_initial'),
        ('devices', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipmentgpstracker',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='equipment.company'),
        ),
       
        migrations.AddField(
            model_name='equipmentgpstracker',
            name='main_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='devices.maincategory'),
        ),
        migrations.AddField(
            model_name='equipmentdevice',
            name='equipment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='equipment.equipment'),
        ),
        migrations.AddField(
            model_name='equipmentdevice',
            name='equipment_gps_tracker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='devices.equipmentgpstracker'),
        ),
        migrations.AddField(
            model_name='equipmentdevice',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user'),
        ),
   
    ]