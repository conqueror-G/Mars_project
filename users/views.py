from django.shortcuts import render

# Create your views here.
import json

import bcrypt
import jwt
from django.http            import JsonResponse
from django.views           import View
from django.core.exceptions import ValidationError 
from django.http            import HttpResponse

from core.utils     import login_decorator
from musma.settings import SECRET_KEY,ALGORITHM
from users.models   import User,Alert

def index(request):
    return render(request, 'index.html', context={'text' : 'web socket'})
    
class SignupView(View): 
    def post(self,request):
        try:
            data                 = json.loads(request.body)   
            name                 = data['name'] 
            identity             = data['identity'] 
            password             = data['password']
            is_location_control  = data['is_location_control']
            is_equipment_control = data['is_equipment_control']
            
            User.objects.create(
                name                 = name,
                identity             = identity,
                is_location_control  = is_location_control,
                is_equipment_control = is_equipment_control,
                password             = bcrypt.hashpw(password.encode('utf-8'),\
                bcrypt.gensalt()).decode('utf-8'),
            )
            return JsonResponse({"message" : "SUCCESS"}, status = 201)
        
        except KeyError:
            return JsonResponse({"message" : "KEY_ERROR"}, status = 400)
        except ValidationError as e :
            return JsonResponse({'message' : e.message }, status = 400)

class SigninView(View):
    def post(self,request):
        try: 
            data     = json.loads(request.body)
            identity = data['identity']
            password = data['password']
            
            if not User.objects.filter(identity = identity).exists():
                return JsonResponse({"message":"INVALID_USER"}, status = 401)
            
            user = User.objects.get(identity = identity)
            
            if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                return JsonResponse({"message" : "INVALID_USER"}, status = 401)
            
            token  = jwt.encode({'user_id' : user.id}, SECRET_KEY, ALGORITHM)
            
            return JsonResponse({ "name"               : user.name,
                                  "isLocationControl"  : user.is_location_control,
                                  "isEquipmentControl" : user.is_equipment_control,
                                  "accessToken"        : token },status=200)
        except KeyError: 
            return JsonResponse({"message" : "KEY_ERROR"},status=400)

class AlertView(View):
    @login_decorator
    def get(self,request):
        user = request.user

        result = {
            "rowBattery" : [
            { 
                "id"                 : rowbattery.id,
                "date"               : rowbattery.created_at,
                "deviceId"           : rowbattery.equipment_gps_tracker.id,
                "deviceSerialNumber" : rowbattery.equipment_gps_tracker.serial_number,
                "alert"              : "rowBattery"
            } for rowbattery in Alert.objects.filter(user_id=user.id,is_low_battery=True)
            ],
            "networkError" : [
            {
                "id"                 : networkerror.id,
                "date"               : networkerror.created_at,
                "deviceId"           : networkerror.equipment_gps_tracker.id,
                "deviceSerialNumber" : networkerror.equipment_gps_tracker.serial_number,
                "alert"              : "networkError"
            } for networkerror in Alert.objects.filter(user_id=user.id,is_network_error=True)
            ] 
        }
        return JsonResponse({'result': result}, status=200)
        
    @login_decorator
    def delete(self,request):
        user     = request.user
        alert_id = request.GET.get('alert_id')
        
        if not Alert.objects.filter(id = alert_id, user = user).exists(): 
            return JsonResponse({'message':'DOES_NOT_EXIST'}, status = 400)

        alert = Alert.objects.get(id = alert_id)
        alert.delete()

        return HttpResponse(status = 204)

        
