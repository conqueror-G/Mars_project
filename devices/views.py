import json
from decimal import Decimal
from os import device_encoding

from django.views     import View
from django.http      import JsonResponse, HttpResponse

from users.models     import History
from devices.models   import EquipmentGpsTracker, Category, EquipmentDevice, EquipmentGpsTrackerRealtime
from equipment.models import Equipment

from core.utils     import login_decorator
from musma.settings import SECRET_KEY,ALGORITHM

class CategoryView(View):
    def get(self, request):        
        categories = Category.objects.all()

        results = [
        {
            "mainCategoryName" : category.main_category.name,
            "subCategory"      : [
                {
                    "id"              : int(category.id),
                    "subCategoryName" : category.name
          }
          ]
        }for category in categories
        ]
        return JsonResponse({"nav": results}, status=200)

class DeviceDetailView(View):
    def get(self, request, equipment_gps_tracker_id):
        try:
            if request.method == "GET":            
                device            = EquipmentGpsTracker.objects.get(id=equipment_gps_tracker_id)
                equipment_devices = EquipmentDevice.objects.filter(equipment_gps_tracker_id=equipment_gps_tracker_id,is_matched=True)
                
                results = {   
                    'id'                       : int(device.id),
                    'serialNumber'             : device.serial_number,
                    'qrCode'                   : device.qr_code,   
                    'company'                  : device.company.name,
                    'device_other_info'        : [{
                        'status'                     : device_other_info.status.content,
                        'lastUpdateTime'             : device_other_info.updated_at,
                        'error'                      : device_other_info.error.content,
                        'statellitesUsed'            : device_other_info.statellites_used,
                        'lowBattery'                 : Decimal(device_other_info.battery),
                        'latitude'                   : device_other_info.latitude,
                        'longitude'                  : device_other_info.longitude
                    }for device_other_info in device.equipmentgpstrackerrealtime_set.all()],

                         'matchedEquipment'    : [ 
                        {     
                        'matchedEquipmentOriginalId' : equipment_device.equipment.original_id,
                        'matchedEquipmentCategory'   : equipment_device.equipment.equipment_category.name,
                        'matchedEquipmentType'       : equipment_device.equipment.equipment_type.name    
                }for equipment_device in equipment_devices]
                }
                return JsonResponse({'results' : results}, status = 200)
        except EquipmentGpsTracker.DoesNotExist:
            return JsonResponse({'message' : 'DEVICE_DOES_NOT_EXIST'}, status = 400)

    @login_decorator
    def patch(self, request, equipment_gps_tracker_id):
        try:
            if request.method == "PATCH":
                data   = json.loads(request.body)
                user   = request.user

                if not user.is_equipment_control == True :
                    return JsonResponse ({'message':'ACCESS_DENIED'}, status=400)

                device            = EquipmentGpsTracker.objects.get(id = equipment_gps_tracker_id)

                device.company_id       = data['company_id']
                device.serial_number    = data['serial_number'] 
                device.qr_code          = data['qr_code']                            
                device.save()

                return JsonResponse({'message' : 'EDIT_SUCCESSED'}, status=200)
        except KeyError:
            return JsonResponse ({'message' : 'KEY_ERROR'}, status=400)

class DeviceDetailHistoryView(View):
    def get(self, request, equipment_gps_tracker_id):
        try:
            order_key = request.GET.get('order', None)
            order_set = {
                'latestHistory': '-date',
                'oldestHistory': 'date'
            }
            order     = order_set.get(order_key, 'id')
            limit     = int(request.GET.get('limit', 10))
            offset    = int(request.GET.get('offset', 0))

            histories = History.objects.filter(equipment_gps_tracker_id=equipment_gps_tracker_id).order_by(order)[offset:offset+limit]
            results   = [
                {
                'id'                                  : history.id,
                'repaired_sort_content'               : history.repaired_sort.content,
                'repaired_manager_name'               : history.repaired_manager.name,
                'equipment_gps_tracker'               : [
                    {   
                        'serial_number' : device.serial_number
                    } for device in EquipmentGpsTracker.objects.filter(id=history.equipment_gps_tracker_id)
                    ],
                'repaired_purpose_content'            : history.repaired_purpose.content,
                'content'                             : history.content,
                'date'                                : history.date                   
                } for history in histories
            ]
            
            return JsonResponse({'results' : results}, status = 200) 
        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status = 400)
        except History.DoesNotExist:
            return JsonResponse({'message' : 'HISTORY_DOES_NOT_EXIST'}, status = 400)            

    @login_decorator
    def post(self, request, equipment_gps_tracker_id):
        try:
            data          = json.loads(request.body)   
            user          = request.user
            
            if not user.is_equipment_control == True:
                return JsonResponse ({'message':'ACCESS_DENIED'}, status=400) 

            repaired_sort_id = 3
            history = History.objects.create(
                equipment_gps_tracker_id = equipment_gps_tracker_id,
                user_id                  = user.id,
                repaired_sort_id         = repaired_sort_id,
                repaired_manager_id      = data['repaired_manager_id'],
                repaired_purpose_id      = data['repaired_purpose_id'],
                content                  = data['content'],
                date                     = data['date']
            )
            if user.is_equipment_control == True:
                history.save()       
                return JsonResponse ({'message':'HISTORY_POST_SUCCESS'}, status=200)

        except KeyError:
            return JsonResponse ({'message':'KEY_ERROR'}, status=400)

    @login_decorator
    def delete(self, request, pk):
        try:
            if request.method == "DELETE":
                user    = request.user
                history = History.objects.get(pk=pk)

                if not user.is_equipment_control == True :
                    return JsonResponse ({'message':'ACCESS_DENIED'}, status=400)

                if not user.id == history.user_id:
                    return JsonResponse ({'message':'DELETE_ACCESS_DENIED'}, status=400)

                else:
                    history.delete()
                    return JsonResponse({'message': 'DELETE_SUCCESS'}, status=200)

        except KeyError:
            return JsonResponse ({'message':'KEY_ERROR'}, status=400)

class DeviceDetailBatteryView(View):
    def get(self, request, equipment_gps_tracker_id):
        try:
            order_key = request.GET.get('order', None)
            order_set = {
                'latestUpdate': '-updated_at',
                'oldestUpdate': 'updated_at',
                'highBattery' : '-battery',
                'lowBattery'  : 'battery'
            }
            order     = order_set.get(order_key, 'id')
            limit     = int(request.GET.get('limit', 10))
            offset    = int(request.GET.get('offset', 0))
            histories = History.objects.all().order_by(order)[offset:offset+limit]

            results   = [
                {
                'id'                             : history.id,
                'date'                           : history.date,
                'repaired_manager_name'          : history.repaired_manager.name,
                'equipment_gps_tracker'          : [
                    {            
                        'serial_number'          : device.serial_number
                    } for device in EquipmentGpsTracker.objects.filter(id=history.equipment_gps_tracker_id)
                    ],
                'battery' : EquipmentGpsTrackerRealtime.objects.filter(equipment_gps_tracker_id=history.equipment_gps_tracker_id).latest('created_at').battery,
                'lastLogTime'                    : history.updated_at,
                    }
                   for history in histories]

            return JsonResponse({'results' : results}, status = 200) 
        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status = 400)
        except EquipmentGpsTracker.DoesNotExist:
            return JsonResponse({'message' : 'DEVICE_INFO_DOES_NOT_EXIST'}, status = 400)            

    @login_decorator
    def post(self, request, equipment_gps_tracker_id):
        try:
            if request.method == "POST":
                data   = json.loads(request.body)
                user   = request.user

                if not user.is_equipment_control == True :
                    return JsonResponse ({'message':'ACCESS_DENIED'}, status=400)

                repaired_sort_id = 2
                history = History.objects.create(
                    user                     = user,
                    equipment_gps_tracker_id = equipment_gps_tracker_id,
                    repaired_sort_id         = repaired_sort_id,
                    repaired_manager_id      = data['repaired_manager_id'],
                    date                     = data['date']
                    )
                history.save()
                return JsonResponse({'message': 'EDIT_SUCCESSED'}, status=200)
        except KeyError:
            return JsonResponse ({'message':'KEY_ERROR'}, status=400)

    @login_decorator
    def delete(self, request, pk):
        try:
                user    = request.user
                history = History.objects.get(id = pk)

                if not user.is_equipment_control == True :
                    return JsonResponse ({'message':'ACCESS_DENIED'}, status=400)

                if user.is_equipment_control == False :
                    return JsonResponse ({'message':'DELETE_ACCESS_DENIED'}, status=400)

                else:
                    history.delete()    
                    return JsonResponse({'message': 'DELETE_SUCCESS'}, status=200)

        except History.DoesNotExist:
            return JsonResponse({'message' : 'HISTORY_DOES_NOT_EXIST'}, status = 500)     
        except KeyError:
            return JsonResponse ({'message':'KEY_ERROR'}, status=400)

class DeviceListView(View):
    def get(self, request):
        try:
            filter_set = {
                'company'       : 'company_id',
                'matchedStatus' : 'is_matched',
                'powerStatus'   : 'is_power',
                'battery'       : 'equipmentgpstrackerrealtime__battery__lte'
            }
            q       = {filter_set.get(key) : json.loads(value) for key, value in request.GET.items() if key in filter_set.keys()}
            limit   = int(request.GET.get('limit', 10))
            offset  = int(request.GET.get('offset', 0))
            devices = EquipmentGpsTracker.objects.filter(**q)[offset:offset+limit]
            results = [
                {
                'id'               : device.id,
                'serialNumber'     : device.serial_number,
                'deviceCategory'   : device.main_category.name,
                'company'          : device.company.name,
                'status'           : device.is_power,
                'matchedStatus'    : device.is_matched,
                'matchedEquipment' : [
                    {
                        'matchedEquipmentId'       : equipment.equipment.original_id,
                        'matchedEquipmentCategory' : equipment.equipment.equipment_category.name
                    } for equipment in device.equipmentdevice_set.all()
                ],         
                'battery'         : device.equipmentgpstrackerrealtime_set.latest('created_at').battery
            
                    } for device in devices ]

            return JsonResponse({'results' : results}, status = 200) 
        except KeyError:
            return JsonResponse({'message' : 'keyError'}, status = 400)
        except EquipmentGpsTracker.DoesNotExist :
            return JsonResponse({'message' : 'deviceDoesNotExist'}, status = 400)

    @login_decorator
    def delete(self, request):
        user = request.user
        ID = {
            'ids' : 'id__in'
        }

        q = {ID.get(key) : json.loads(value) for key, value in request.GET.items() if key in ID.keys()}

        if not EquipmentGpsTracker.objects.filter(**q).exists() : 
            return JsonResponse({'message':'DOES_NOT_EXIST'}, status = 400)
            
        if not user.is_equipment_control == True :
            return JsonResponse({"message" : "NO_PERMISSION"}, status=401)        
        device = EquipmentGpsTracker.objects.filter(**q)
        device.delete()

        return HttpResponse(status = 204)

class DeviceDetailSetUpView(View):
    def get(self, request, equipment_gps_tracker_id):
        try:
            order            = '-updated_at'
            limit            = int(request.GET.get('limit', 10))
            offset           = int(request.GET.get('offset', 0))
            equipmentdevices = EquipmentDevice.objects.filter(equipment_gps_tracker_id=equipment_gps_tracker_id).order_by(order)[offset:offset+limit]
            results          = [
                {
                'id'                    : equipmentdevice.id,
                'lastUpdateTime'        : equipmentdevice.updated_at,
                'deviceSerialNumber'    : equipmentdevice.equipment_gps_tracker.serial_number,
                'equipmentSerialNumber' : equipmentdevice.equipment.original_id,
                'matchedUserId'         : equipmentdevice.user.identity,
                'matchedStatus'         : equipmentdevice.is_matched            
                } for equipmentdevice in equipmentdevices
            ]
            return JsonResponse({'results' : results}, status = 200) 
        except EquipmentDevice.DoesNotExist:
            return JsonResponse({'message' : 'EQUIPMENT_DEVICE_DOES_NOT_EXIST'}, status = 400)