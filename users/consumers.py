import json

from random import randint
from time   import sleep

from channels.generic.websocket import WebsocketConsumer

from devices.models import (
    EquipmentGpsTrackerRealtime,
    EquipmentGpsTracker,
    EquipmentDevice
)
from users.models   import Alert

class WSConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
    
        for i in range(9,11):
            battery          = randint(500,2000)
            statellites_used = randint(10,12)
            status           = randint(1,3)

            # battery          = 500
            # statellites_used = randint(10,12)
            # status           = 3

            equipment_gps_tracker = EquipmentGpsTracker.objects.get(id=i).id

            equipment_gps_tracker_realtime = EquipmentGpsTrackerRealtime.objects.create(
                equipment_gps_tracker_id = equipment_gps_tracker,
                status_id                = status,
                statellites_used         = statellites_used,
                battery                  = battery*0.025,
            )
            equipment_gps_tracker_realtime.save()

            if EquipmentDevice.objects.filter(equipment_gps_tracker_id=equipment_gps_tracker).exists(): 
                if battery*0.025 <= 20:
                    alerts = Alert.objects.create(
                        equipment_gps_tracker_id = equipment_gps_tracker,
                        is_low_battery           = 'True',
                        user_id                  = EquipmentDevice.objects.get(equipment_gps_tracker_id=equipment_gps_tracker,is_matched=True).user.id,
                        is_network_error         = 'False',
                    )
                    alerts.save()


                    self.send(json.dumps({'message' : equipment_gps_tracker.serial_number}))

                if status == 3:
                    alerts = Alert.objects.create(
                        equipment_gps_tracker_id = equipment_gps_tracker,
                        is_low_battery           = 'False',
                        user_id                  = EquipmentDevice.objects.get(equipment_gps_tracker_id=equipment_gps_tracker,is_matched=True).user.id,
                        is_network_error         = 'True',
                    )
                    alerts.save()
                    self.send(json.dumps({'message' : equipment_gps_tracker}))

            sleep(1)
