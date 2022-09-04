
import json

from django.db.models import Count
from django.http      import JsonResponse
from django.views     import View
from django.http      import HttpResponse

from core.utils import login_decorator

from equipment.models import Equipment, Driver
from users.models     import History, RepairedPurpose
from devices.models   import (
    EquipmentDevice, 
    EquipmentGpsTracker, 
    EquipmentGpsTrackerRealtime
)

class EquipmentRegisteredView(View):
    @login_decorator
    def post(self,request):
        try:
            data = json.loads(request.body)
            user = request.user

            if not user.is_equipment_control == True :
                return JsonResponse({"message" : "NO_PERMISSION"}, status=401)

            equipment_category_id            = data['equipment_category_id']
            equipment_type_id                = data['equipment_type_id']
            maintenance_company              = data['maintenance_company']
            maintenance_manager_name         = data['maintenance_manager_name']
            maintenance_manager_phone_number = data['maintenance_manager_phone_number']
            maintenance_manager_department   = data['maintenance_manager_department']
            company_id                       = data['company_id']
            plate_number                     = data['plate_number']
            original_id                      = data['original_id']
            unit_id                          = data['unit_id']
            capacity                         = data['capacity']
            qr_code                          = data['qr_code']
            manufacture_date                 = data['manufacture_date']
            driver_id                        = data['driver_id']

            if Equipment.objects.filter(original_id=original_id).exists(): 
                return JsonResponse({'message':'ORIGNAL_ID_NUMBER_EXIST'}, status = 400)
            
            if Equipment.objects.filter(plate_number=plate_number).exists(): 
                return JsonResponse({'message':'PLATE_NUMBER_EXIST'}, status = 400)

            if Equipment.objects.filter(qr_code=qr_code).exists(): 
                return JsonResponse({'message':'QR_CODE_EXIST'}, status = 400)

            equipment = Equipment.objects.create(
                main_category_id                 = 1,
                equipment_category_id            = equipment_category_id,
                equipment_type_id                = equipment_type_id,
                maintenance_company              = maintenance_company,
                maintenance_manager_name         = maintenance_manager_name,
                maintenance_manager_phone_number = maintenance_manager_phone_number,
                maintenance_manager_department   = maintenance_manager_department,
                company_id                       = company_id,
                original_id                      = original_id,
                unit_id                          = unit_id,
                capacity                         = capacity,
                qr_code                          = qr_code,
                plate_number                     = plate_number,
                manufacture_date                 = manufacture_date,
                driver_id                        = driver_id
                )
            equipment.save()
            
            return JsonResponse({'message' : 'SUCCESS'}, status= 201)
        except Equipment.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_UPDATE'}, status= 404)

class EquipmentdetailView(View):
    def get(self,request, equipment_id):
        try:
            equipment         = Equipment.objects.get(id=equipment_id)
            equipment_devices = EquipmentDevice.objects.filter(equipment_id=equipment_id)
            historyies        = History.objects.filter(equipment_id=equipment_id)
            limit             = int(request.GET.get('limit', 10))
            offset            = int(request.GET.get('offset', 0))

            company  = {
                    'id'   : equipment.company.id,
                    'name' : equipment.company.name,
                }

            device = [
                {
                    'id'           : equipment_device.equipment_gps_tracker.id,
                    'battery'      : EquipmentGpsTrackerRealtime.objects.filter(equipment_gps_tracker_id=equipment_device.equipment_gps_tracker.id).latest('created_at').battery,
                    'lastLogTime'  : EquipmentGpsTrackerRealtime.objects.filter(equipment_gps_tracker_id=equipment_device.equipment_gps_tracker.id).latest('created_at').updated_at,
                    'longitude'    : EquipmentGpsTrackerRealtime.objects.filter(equipment_gps_tracker_id=equipment_device.equipment_gps_tracker.id).latest('created_at').longitude,
                    'latitude'     : EquipmentGpsTrackerRealtime.objects.filter(equipment_gps_tracker_id=equipment_device.equipment_gps_tracker.id).latest('created_at').latitude,
                    'serialNumber' : equipment_device.equipment_gps_tracker.serial_number,
                    'manager'      : {
                        'id'   : equipment_device.user.id,
                        'name' : equipment_device.user.name,
                    },
                    'company' : {
                        'id'   : equipment_device.equipment_gps_tracker.company.id,
                        'name' : equipment_device.equipment_gps_tracker.company.name,
                    }
                } for equipment_device in equipment_devices.filter(is_matched=True)
            ]

            unit  = {
                    'id'   : equipment.unit.id,
                    'name' : equipment.unit.name
                }

            equipment_type  = {
                    'id'   : equipment.equipment_type.id,
                    'name' : equipment.equipment_type.name
                } 

            equipment_category  = {
                    'id'       : equipment.equipment_category.id,
                    'name'     : equipment.equipment_category.name,
                    'imageUrl' : equipment.equipment_category.image_url
                }    

            repaired_history = [
                {
                'id'   : history.id,
                'sort' : {
                    'id'      : history.repaired_sort.id,
                    'content' : history.repaired_sort.content
                },
                'manager' : {
                    'id'      : history.repaired_manager.id, 
                    'name'    : history.repaired_manager.name,
                    'company' : history.repaired_manager.repaired_company.name
                },
                'repairedPurpose' : [
                    {
                    'id'      : repaired_purpose.id, 
                    'content' : repaired_purpose.content, 
                } for repaired_purpose in RepairedPurpose.objects.filter(history__id=history.id)
                ],
                'date'    : history.date,
                'content' : history.content
            } for history in historyies.filter(repaired_sort_id=3)[offset:offset+limit]
            ]

            matched_history = [
                {
                    'id'           : equipment_device.equipment_gps_tracker.id,
                    'lastLogTime'  : equipment_device.equipment_gps_tracker.updated_at,
                    'serialNumber' : equipment_device.equipment_gps_tracker.serial_number,
                    'manager'      : {
                        'id'   : equipment_device.user.id,
                        'name' : equipment_device.user.name,
                    },
                    'company' : {
                        'id'   : equipment_device.equipment_gps_tracker.company.id,
                        'name' : equipment_device.equipment_gps_tracker.company.name,
                    }
                } for equipment_device in equipment_devices[offset:offset+limit]
            ]

            equipment = {
                'id'                               : equipment.id,
                'company'                          : company,
                'maintenance_company'              : equipment.maintenance_company,
                'maintenance_manager_name'         : equipment.maintenance_manager_name,
                'maintenance_manager_phone_number' : equipment.maintenance_manager_phone_number,
                'maintenance_manager_department'   : equipment.maintenance_manager_department,
                'unit'                             : unit,
                'capacity'                         : equipment.capacity,
                'equipmentType'                    : equipment_type,
                'equipmentCategory'                : equipment_category,
                'repaired_history'                 : repaired_history,
                'matched_history'                  : matched_history,
                'device'                           : device,
                'plateNumber'                      : equipment.plate_number,
                'manufactureDate'                  : equipment.manufacture_date,
                'qrCode'                           : equipment.qr_code,
                'isPower'                          : equipment.is_power,
                'originalId'                       : equipment.original_id,
                "driver" : [
                    {
                        "id"      : driver.id,
                        "name"    : driver.name,
                        "level"   : driver.level.name,
                        "company" : driver.driver_company.name,
                    } for driver in Driver.objects.filter(id=equipment.driver_id)
                ]
                } 

            return JsonResponse({'equipment' : equipment}, status = 200)
        except Equipment.DoesNotExist:
            return JsonResponse({'message' : 'DOES_NOT_EXIST'}, status= 404)

    @login_decorator
    def patch(self,request,equipment_id):
        try:
            data = json.loads(request.body)
            user = request.user
            print(request.body)

            if not user.is_equipment_control == True :
                return JsonResponse({"message" : "NO_PERMISSION"}, status=401)

            equipment = Equipment.objects.get(id=equipment_id)

            equipment.equipment_category_id            = data['equipment_category_id']
            equipment.equipment_type_id                = data['equipment_type_id']
            equipment.maintenance_company              = data['maintenance_company']
            equipment.maintenance_manager_name         = data['maintenance_manager_name']
            equipment.maintenance_manager_phone_number = data['maintenance_manager_phone_number']
            equipment.maintenance_manager_department   = data['maintenance_manager_department']
            equipment.company_id                       = data['company_id']
            equipment.plate_number                     = data['plate_number']
            equipment.original_id                      = data['original_id']
            equipment.unit_id                          = data['unit_id']
            equipment.capacity                         = data['capacity']
            equipment.qr_code                          = data['qr_code']
            equipment.manufacture_date                 = data['manufacture_date']
            equipment.driver_id                        = data['driver_id']
    
            equipment.save()
            
            return JsonResponse({'message' : 'SUCCESS'}, status= 201)
        except Equipment.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_UPDATE'}, status= 404)

    @login_decorator
    def post(self,request, equipment_id):
        try:
            data = json.loads(request.body)
            user = request.user.id

            content             = data['content']
            date                = data['date']
            repaired_sort_id    = 3
            repaired_purpose_id = data['repaired_purpose_id']
            repaired_manager_id = data['repaired_manager_id']
 
            history = History.objects.create(
                user_id             = user,
                equipment_id        = equipment_id,
                content             = content,
                date                = date,
                repaired_manager_id = repaired_manager_id,
                repaired_sort_id    = repaired_sort_id,
                repaired_purpose_id = repaired_purpose_id,
                )
    
            history.save()
            
            return JsonResponse({'message' : 'SUCCESS'}, status= 201)
        except Equipment.DoesNotExist:
            return JsonResponse({'message' : 'DOES_NOT_EXIST'}, status= 404)
    
    @login_decorator
    def delete(self, request, equipment_id):
        data        = json.loads(request.body)
        user_id     = request.user.id
        history_id  = data['history_id']
        
        if not History.objects.filter(id=history_id, equipment_id=equipment_id,user_id=user_id).exists(): 
            return JsonResponse({'message':'DOES_NOT_EXIST'}, status = 404)
        
        history = History.objects.filter(id=history_id, user_id=user_id)
        history.delete()

        return HttpResponse(status = 204)

class DeviceRegisteredView(View):
    @login_decorator
    def post(self,request):
        try:
            data = json.loads(request.body)
            user = request.user

            if not user.is_equipment_control == True and not user.is_location_control == True :
                return JsonResponse({"message" : "NO_PERMISSION"}, status=401)

            company_id    = data['company_id']
            qr_code       = data['qr_code']
            serial_number = data['serial_number']

            if EquipmentGpsTracker.objects.filter(serial_number=serial_number).exists(): 
                return JsonResponse({'message':'SERIAL_NUMBER_EXIST'}, status = 400)
            
            if EquipmentGpsTracker.objects.filter(qr_code=qr_code).exists(): 
                return JsonResponse({'message':'QR_CODE_EXIST'}, status = 400)
 
            equipment_gps_tracker = EquipmentGpsTracker.objects.create(
                main_category_id = 2,
                company_id       = company_id,
                qr_code          = qr_code,
                serial_number    = serial_number
                )
            equipment_gps_tracker.save()
            
            return JsonResponse({'message' : 'SUCCESS'}, status= 201)
        except Equipment.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_REGISTERED'}, status= 404)

class EquipmentListView(View):
    def get(self, request):
        sort = request.GET.get('sort','id')
        
        FILTER_SET = {
            'type_id'   : 'equipment_type_id',
            'status_id' : 'equipmentdevice__equipment_gps_tracker_id__equipmentgpstrackerrealtime__status_id',
            'battery'   : 'equipmentdevice__equipment_gps_tracker_id__equipmentgpstrackerrealtime__battery__lte',
            'is_power'  : 'is_power'
        }

        SORT_SET = {
            'id'           : 'id',
            'low_battery'  : 'equipmentdevice__equipment_gps_tracker_id__equipmentgpstrackerrealtime__battery',
            'high_battery' : '-equipmentdevice__equipment_gps_tracker_id__equipmentgpstrackerrealtime__battery'
        }

        q = {FILTER_SET.get(key) : json.loads(value) for key, value in request.GET.items() if key in FILTER_SET.keys()}

        equipments = Equipment.objects.filter(**q).order_by(SORT_SET[sort])

        equipment = [
            {
            'id'            : equipment.id,
            'company'       : equipment.company.name,
            'equipmentId'   : equipment.equipment_type.id,
            'equipmentType' : equipment.equipment_type.name, 
            'deviceMatched' : [
                {
                    'isMatched' : equipment_device.is_matched
                }for equipment_device in EquipmentDevice.objects.filter(equipment_id=equipment.id,is_matched=True)
            ],
            'deviceStatus' : [
                {   'battery'       : EquipmentGpsTrackerRealtime.objects.filter(equipment_gps_tracker_id=equipment_device.equipment_gps_tracker.id).latest('created_at').battery,
                    'statusId'      : EquipmentGpsTrackerRealtime.objects.filter(equipment_gps_tracker_id=equipment_device.equipment_gps_tracker.id).latest('created_at').status.id,
                    'statusContent' : EquipmentGpsTrackerRealtime.objects.filter(equipment_gps_tracker_id=equipment_device.equipment_gps_tracker.id).latest('created_at').status.content
                } for equipment_device in EquipmentDevice.objects.filter(equipment_id=equipment.id,is_matched=True)
            ],
            'isPower'    : equipment.is_power,
            'originalId' : equipment.original_id,
            'qrCode'     : equipment.qr_code,
            'driver'   : [
                {
                    "driver_id"   : driver.id,
                    "driver_name" : driver.name,
                } for driver in Driver.objects.filter(id=equipment.driver_id)
            ]
            } for equipment in equipments
        ]
        
        return JsonResponse({"results" : equipment}, status = 200)
    
    @login_decorator
    def delete(self, request):
        user = request.user

        ID = {
            'ids' : 'id__in'
        }

        q = {ID.get(key) : json.loads(value) for key, value in request.GET.items() if key in ID.keys()}

        if not Equipment.objects.filter(**q).exists(): 
            return JsonResponse({'message':'DOES_NOT_EXIST'}, status = 400)

        if not user.is_equipment_control == True :
            return JsonResponse({"message" : "NO_PERMISSION"}, status=401)
        
        for key, equipments in q.items():
            if key == 'id__in':
                for equipment in equipments:
                    if EquipmentDevice.objects.filter(equipment_id=equipment,is_matched=True).exists():
                        equipment_device      = EquipmentDevice.objects.get(equipment_id=equipment,is_matched=True)
                        equipment_gps_tracker = EquipmentGpsTracker.objects.get(id = equipment_device.equipment_gps_tracker_id)
                        equipment_gps_tracker.is_matched = False
                        equipment_gps_tracker.save()

        equipment = Equipment.objects.filter(**q)
        equipment.delete()

        return HttpResponse(status = 204)

class MatchView(View):
    @login_decorator
    def get(self,request) :
        user   = request.user

        equipments             = Equipment.objects.all()
        equipment_gps_trackers = EquipmentGpsTracker.objects.all()

        if not user.is_equipment_control == True :
            return JsonResponse({"message" : "NO_PERMISSION"}, status=401)
            
        equipment  = [
            {
                'id'            : equipment.id,
                'originalId'    : equipment.original_id,
                'companyName'   : equipment.company.name,
                'equipmentType' : equipment.equipment_type.name,
                'isMatched'     : [
                    {
                        'isMatched' : equipment_gps_tracker.equipment_gps_tracker.is_matched
                    }for equipment_gps_tracker in EquipmentDevice.objects.filter(equipment_id=equipment.id,is_matched=True)
                ]
            }for equipment in equipments
            ]
        equipment_gps_tracker  = [
            {
                'id'           : equipment_gps_tracker.id,
                'battery'      : EquipmentGpsTrackerRealtime.objects.filter(equipment_gps_tracker_id=equipment_gps_tracker.id).latest('created_at').battery,
                'status'       : EquipmentGpsTrackerRealtime.objects.filter(equipment_gps_tracker_id=equipment_gps_tracker.id).latest('created_at').status.content,
                'serialNumber' : equipment_gps_tracker.serial_number,
                'companyName'  : equipment_gps_tracker.company.name,
                'isMatched'    : equipment_gps_tracker.is_matched
            }for equipment_gps_tracker in equipment_gps_trackers
            ]
        result ={
            'equipment'           : equipment,
            'equipmentGpsTracker' : equipment_gps_tracker
        }
        return JsonResponse({"results" : result}, status = 200)

    @login_decorator
    def post(self,request):
        user = request.user

        equipment_id             = request.GET.get("equipment_id")
        equipment_gps_tracker_id = request.GET.get("equipment_gps_tracker_id")
        
        if not user.is_equipment_control == True :
            return JsonResponse({"message" : "NO_PERMISSION"}, status=401)
        
        if EquipmentDevice.objects.filter(equipment_id=equipment_id,is_matched=True).exists(): 
            equipment_device  = EquipmentDevice.objects.get(equipment_id=equipment_id,is_matched=True)
            equipment_device.is_matched = False
            equipment_device.save()

            equipment_gps_tracker = equipment_device.equipment_gps_tracker
            equipment_gps_tracker.is_matched = False
            equipment_gps_tracker.save()
        
        if EquipmentDevice.objects.filter(equipment_gps_tracker_id=equipment_gps_tracker_id,is_matched=True).exists(): 
            equipment_device  = EquipmentDevice.objects.get(equipment_gps_tracker_id=equipment_gps_tracker_id,is_matched=True)
            equipment_device.is_matched = False
            equipment_device.save()
        
        equipment_device = EquipmentDevice.objects.create(
            user_id                   = user.id,
            equipment_id              = equipment_id,
            equipment_gps_tracker_id  = equipment_gps_tracker_id,
            is_matched                = True
            )
        equipment_device.save()

        equipment_gps_tracker = EquipmentGpsTracker.objects.get(id=equipment_gps_tracker_id)
        equipment_gps_tracker.is_matched = True
        equipment_gps_tracker.save()

        return JsonResponse({'message' : "SUCCESS"}, status = 201)

    @login_decorator
    def delete(self,request ):
        user         = request.user
        equipment_id = request.GET.get("equipment_id")  

        if not user.is_equipment_control == True :
            return JsonResponse({"message" : "NO_PERMISSION"}, status=401)
            
        equipment_device = EquipmentDevice.objects.get(equipment_id = equipment_id,is_matched=True)
        equipment_device.is_matched = False
        equipment_device.save()

        equipment_gps_tracker = equipment_device.equipment_gps_tracker
        equipment_gps_tracker.is_matched = False
        equipment_gps_tracker.save()
        
        return HttpResponse(status = 204)

class AdminListView(View):
    @login_decorator
    def get(self, request):
        user = request.user
        equipment_devices = EquipmentDevice.objects.all()
        historyies        = History.objects.all()

        if not user.is_equipment_control == True :
            return JsonResponse({"message" : "NO_PERMISSION"}, status=401)

        equipment_repaired = [
            {
                'sortType'      : 'equipment_repaired',
                'equipmentId'   : history.equipment.id,
                'date'          : history.created_at,
                'equipmentType' : history.equipment.equipment_type.name,
                'originalId'    : history.equipment.original_id
            }for history in historyies.filter(repaired_sort_id=3,equipment_gps_tracker_id__isnull = True )
        ]

        equipment_matched = [
            {
                'sortType'         : 'equipment_matched',
                'equipmentId'      : equipment_device.id,
                'date'             : equipment_device.created_at,
                'equipmentCompany' : equipment_device.equipment.company.name,
                'originalId'       : equipment_device.equipment.original_id
            }for equipment_device in equipment_devices.filter(is_matched=True)
        ]

        device_repaired =[
            {
                'sortType'      : 'device_repaired',
                'id'            : history.id,
                'date'          : history.created_at,
                'deviceCompany' : history.equipment_gps_tracker.company.name,
                'serialNumber'  : history.equipment_gps_tracker.serial_number
            }for history in historyies.filter(repaired_sort_id=3,equipment_id__isnull = True )
        ]

        device_battery_repaired=[
            {
                'sortType'      : 'device_battery_replacement',
                'id'            : history.id,
                'date'          : history.created_at,
                'deviceCompany' : history.equipment_gps_tracker.company.name,
                'serialNumber'  : history.equipment_gps_tracker.serial_number
            }for history in historyies.filter(repaired_sort_id=2,equipment_id = None )
        ]

        result = { 
            'equipmentRepaired'     : equipment_repaired,
            'equipmentMatched'      : equipment_matched,
            'deviceRepaired'        : device_repaired,
            'deviceBatteryRepaired' : device_battery_repaired
        }
        
        return JsonResponse({"results" : result}, status = 200)
       
class HomeView(View):
    def get(self, request):
        equipment_gps_trackers    = EquipmentGpsTracker.objects.all()
        equipment_devices         = EquipmentDevice.objects.all()
        equipment_device_realtime = EquipmentGpsTrackerRealtime.objects.all()
        equipments_power          =  Equipment.objects.filter(is_power=True)
        equipment_device          = equipment_devices.filter(is_matched=True)
        equipments_activate       = [ equipments_power.filter(id=device.id) for device in equipment_device]

        device_total_count  = [ i for i in equipment_gps_trackers.aggregate(count=Count('id')).values()] 
        device_matched      = [ i for i in equipment_gps_trackers.filter(is_matched=True).aggregate(count=Count('id')).values()] 

        device_low_battey_count     = len(set([ i for i in equipment_gps_trackers.filter(equipmentgpstrackerrealtime__battery__lte=20)]))
        equipment_low_battery_count = len(set([ i for i in equipment_gps_trackers.filter(is_matched=True,equipmentgpstrackerrealtime__battery__lte=20)]))
        device_power_count          = len([ equipment_gps_trackers.filter(is_matched=True)]) 

        RSSI    = [equipment_device_realtime.filter(equipment_gps_tracker_id=equipment_gps_tracker.id).latest('created_at').statellites_used for equipment_gps_tracker in equipment_gps_trackers]
        devices = [equipment_device_realtime.filter(equipment_gps_tracker_id=equipment_gps_tracker.id).latest('created_at').id for equipment_gps_tracker in equipment_gps_trackers.filter(is_matched=True)]

        results = { 
            "count" : [
                {
                    "equipmentActive" :[
                        {
                            "activate"   : len(equipments_activate)
                        },
                        {
                            "inactivate" : device_matched[0] - len(equipments_activate)
                        },
                        {
                            "Total"      : device_matched[0]
                        }
                        ,
                    ], 
                    "equipmentOnline" :
                    [ 
                        {
                            "success" : device_power_count
                        },
                        {
                            "fail"    : device_matched[0] - device_power_count
                        },
                        {
                            "Total"   : device_matched[0]
                        },
                    ],
                    "batteryReplacePeriod" :
                    [  
                        {
                            "unexpired" : len(equipment_device) - equipment_low_battery_count
                        },
                        {
                            "expired"   : equipment_low_battery_count
                        },
                        {
                            "Total"     : len(equipment_device)
                        },
                    ],
                    "deviceMatch" :
                    [ 
                        {
                            "matched"   : device_matched[0]
                        },
                        {
                            "unMatched" : device_total_count[0]-device_matched[0]
                        },
                        {
                            "Total"     : device_total_count[0]
                        },
                    ],
                    "deviceBattery" :
                    [
                        {
                            "LowBattery" : device_low_battey_count
                        },
                    ],
                    "RSSI":
                    [
                        { 
                            "strong" : RSSI.count(12)
                        },
                        {
                            "normal" : RSSI.count(11)
                        },
                        {
                            "weak"   : RSSI.count(10)
                        }
                    ]
                }
            ],
            "powerOn" : 
             [
                {   "equipment" : [
                    {
                        "equipmentId"   : equipment_device.equipment.id,
                        "equipmentType" : equipment_device.equipment.equipment_type.name,
                        "isPower"       : equipment_device.equipment.is_power,
                    } for equipment_device in equipment_devices.filter(equipment_gps_tracker_id=realtime.equipment_gps_tracker.id,is_matched=True)
                ],
                    "latitude"  : realtime.latitude,
                    "longitude" : realtime.longitude,
                } for device in devices 
                for realtime in equipment_device_realtime.filter(id=device,status_id=1)
            ],
            "networkError" : 
             [
                {   
                    "equipment" : [
                    {
                        "equipmentId"   : equipment_device.equipment.id,
                        "equipmentType" : equipment_device.equipment.equipment_type.name,
                        "isPower"       : equipment_device.equipment.is_power,
                    } for equipment_device in equipment_devices.filter(equipment_gps_tracker_id=realtime.equipment_gps_tracker.id,is_matched=True)
                ],
                    "latitude"  : realtime.latitude,
                    "longitude" : realtime.longitude,
                } for device in devices 
                for realtime in equipment_device_realtime.filter(id=device,status_id=3)
            ],
            "networkOff" : 
             [
                {   
                    "equipment" : [
                    {
                        "equipmentId"   : equipment_device.equipment.id,
                        "equipmentType" : equipment_device.equipment.equipment_type.name,
                        "isPower"       : equipment_device.equipment.is_power,
                    } for equipment_device in equipment_devices.filter(equipment_gps_tracker_id=realtime.equipment_gps_tracker.id,is_matched=True)
                ],
                    "latitude"  : realtime.latitude,
                    "longitude" : realtime.longitude,
                } for device in devices 
                for realtime in equipment_device_realtime.filter(id=device,status_id=2)
            ],
        }   

        return JsonResponse({'result' : results}, status = 200)

