from django.http import JsonResponse, HttpResponseRedirect  # HttpResponse,
import pymongo
import json
from bson import json_util
from datetime import datetime

from django.views.decorators.csrf import csrf_protect, csrf_exempt
from pymongo import MongoClient
from rest_framework import status  # viewsets,
import time

import threading
from threading import Thread


try:
    client: MongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
    print('connect database successful.')
except Exception as e:
    print('connect database error.', e)

db = client["slatestdb"]

col = db["slapolicies"]

col_list = db.list_collection_names()
if 'slapolicies' in col_list:
    print("The collection exist.")


@csrf_exempt
# http://localhost:8000/api/
def get_data_from_db(request):
    tmp_type = col.find()
    data = json.loads(json_util.dumps(tmp_type))
    return JsonResponse({
        'data': data
    }, status=status.HTTP_200_OK)


@csrf_exempt
# http://localhost:8000/api/insert
def insert_data(request):
    try:
        # timestamp_created = datetime.timestamp(datetime.now())
        data = {
            'name': 'guide2',
            'priority': '1',
            'response_time': '10',
            'created_time': str(time.time()),
            'process_time': '30',
            'status': 'new',
            'department': 'CS',
        }
        ist_data = col.insert_one(data)
        return JsonResponse({
            'data': 'Create a new sla policy successful.'
        }, status=status.HTTP_201_CREATED)
    except Exception as err:
        print("error:", err)
        return JsonResponse({
            'message': 'Create unsuccessful.'
        }, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
# http://localhost:8000/api/update
def update_data(request, result):
    try:
        if request.method == 'POST':
            request_body = json.loads(request.body)
            SLA_time = request_body['SLA_time']
            SLA_time = int(SLA_time) * 60  # SLA_time(seconds)
            process_time = request_body.get('process_time')
            process_time = int(process_time) * 60  # process_time(seconds)
            SLA_name = request_body.get('name')
            department = request_body.get('department')
            temp_data = col.find({'name': SLA_name, 'status': 'pending'})

            data = {
                'name': SLA_name,
                'department': department,
                'response_time': '',
                'process_time': '',
                'status': 'new',
                'result': '',
            }
            data1 = {
                "$set": {
                    'response_time': str(SLA_time),
                    'process_time': str(process_time),
                    'status': 'done',
                    'result': result,
                },
            }
            col.update_one(data, data1)

            return JsonResponse({
                'message': 'Update element successful.'
            }, status=status.HTTP_201_CREATED)
    except Exception as err:
        print("error:", err)


@csrf_exempt
# http://localhost:8000/api/thread1
def get_sla_policy1(request):
    data = {
        'start_time': datetime.now().time(),
        'sla_name': {
            'P1': 'SLA1',
            'P2': 'SLA2',
        },
        'response_time': {
            'SLA1': '10',  # %H:%M:%S
            'SLA2': '20',  # %H:%M:%S
        },
        'result': {
            'SLA1': '5',
            'SLA2': '7',
            're': ('Done', 'Overdue'),
        },
    }

    return JsonResponse({
        'data': data['sla_name']
    }, status=status.HTTP_200_OK)


@csrf_exempt
# http://localhost:8000/api/threading
def threading_task(request):
    try:
        if request.method == 'POST':
            request_body = json.loads(request.body)
            ticket_status = request_body.get('status')
            SLA_time = request_body.get('SLA_time')
            process_time = request_body.get('process_time')
            department = request_body.get('department')

            SLA_time = int(SLA_time) * 60  # SLa time (seconds)
            process_time = int(process_time) * 60  # process time (seconds)
            # Apply threading to runtime timer() and show_result()
            if ticket_status == 'pending':
                # Run async timer to alert escalate message
                thread1 = threading.Thread(target=timer, args=(request, SLA_time, process_time, department))
                thread1.setDaemon(True)
                thread1.start()
            elif ticket_status == 'done':
                # run async function show_result
                thread2 = threading.Thread(target=show_result, args=(request, SLA_time, process_time, department, status))
                thread2.setDaemon(True)
                thread2.start()
            # return JsonResponse({
            #     'message': 'ok'
            # },status=status.HTTP_200_OK)

    except Exception as err:
        print('error: ', err)


@csrf_exempt
# http://localhost:8000/api/result
def show_result(request, *args, **kwargs):
    try:
        if request.method == 'POST':
            request_body = json.loads(request.body)
            SLA_time = request_body.get('SLA_time')
            department = request_body.get('department')
            SLA_name = request_body.get('name')

            SLA_time = int(SLA_time) * 60  # SLA_time(seconds)
            result = ''

            if SLA_time < 0:
                result = result + 'Overdue'
                update_data(request, result)
                print("SLA name: ", SLA_name)
                print("mess: ", result)
                return JsonResponse({
                    'result': result
                },status=status.HTTP_200_OK)
            else:
                if (SLA_time < 300 and department == 'IT') or (SLA_time < 900 and department == 'CS'):
                    result = result + 'Done and Escalated'
                    update_data(request, result)
                    print("SLA name: ", SLA_name)
                    print("mess: ", result)
                    return JsonResponse({
                        'result': result
                    }, status=status.HTTP_200_OK)
                else:
                    result = result + 'Done'
                    update_data(request, result)
                    print("SLA name: ", SLA_name)
                    print("mess: ", result)
                    return JsonResponse({
                        'result': result
                    }, status=status.HTTP_200_OK)

    except Exception as err:
        print("error", err)


@csrf_exempt
# http://localhost:8000/api/timer
def timer(request, *args, **kwargs):
    try:
        if request.method == 'POST':
            request_body = json.loads(request.body)
            name = request_body.get('name')
            SLA_time = request_body.get('SLA_time')
            process_time = request_body.get('process_time')
            department = request_body.get('department')

            SLA_time = int(SLA_time) * 60  # SLa time (seconds)
            process_time = int(process_time) * 60  # process time (seconds)

            while SLA_time >= 0:
                SLA_time = SLA_time - 1
                process_time = process_time + 1
                time.sleep(1)
                print('SLA name: ', name)
                print('SLA time: ', SLA_time)
                print('process time: ', process_time)
                if (0 < SLA_time <= 300 and department == 'IT') or (0 < SLA_time < 900 and department == 'CS'):
                    # return JsonResponse({
                    #     'message': 'Need to escalate'
                    # },status=status.HTTP_200_OK)
                    data = {
                        'SLA_time': SLA_time,
                        'process_time': process_time,
                        'message': 'Need to escalate.'
                    }
                    print('data:', data)
                    # return JsonResponse({
                    #     'data': data
                    # }, status=status.HTTP_200_OK)
                continue
            else:
                ticket_status = request_body.get('status')
                SLA_time = SLA_time - 1
                process_time = process_time + 1
                time.sleep(1)
                print('SLA name: ', name)
                print('SLA time: ', SLA_time)
                print('process time: ', process_time)
                if ticket_status == 'done':
                    pass
            return JsonResponse({
                'message': 'done'
            },status=status.HTTP_200_OK)

    except Exception as err:
        print('error', err)
