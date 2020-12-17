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
            thread_id = 0

            SLA_time = int(SLA_time) * 60  # SLa time (seconds)
            process_time = int(process_time) * 60  # process time (seconds)
            # Apply threading to runtime timer() and show_result()
            if ticket_status == 'new':
                # Run async timer to alert escalate message
                thread1 = threading.Thread(target=timer, args=(request, SLA_time, process_time, department))
                thread1.setDaemon(True)
                thread1.start()
                thread_id = threading.get_ident()
                # thread1.is_alive()
                thread1.join()
                # print(thread1_id)
            elif ticket_status == 'done':
                # run async function show_result
                thread2 = threading.Thread(target=show_result, args=(request, SLA_time, process_time, department, status))
                thread2.setDaemon(True)
                thread2.start()
                thread_id = threading.get_ident()
                # thread2.is_alive()
                # thread2.join()
            return JsonResponse({
                'message': thread_id
            },status=status.HTTP_200_OK)

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
            escalate_time = 0

            if 'IT' in department:
                escalate_time = 300
            elif 'CS' in department:
                escalate_time = 1200

            if (SLA_time and department and SLA_name) is not None:
                if SLA_time < 0:
                    result = result + 'Overdue'
                    update_data(request, result)
                    print("SLA name: ", SLA_name)
                    print("mess: ", result)
                    return JsonResponse({
                        'result': result
                    },status=status.HTTP_200_OK)
                else:
                    if SLA_time <= escalate_time:
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
            else:
                return JsonResponse({
                    'message': 'Oop! Missing something, please check your input again.'
                }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as err:
        print("error", err)


@csrf_exempt
# http://localhost:8000/api/timer
def timer(request, *args, **kwargs):
    try:
        if request.method == 'POST':
            request_body = json.loads(request.body)
            SLA_name = request_body.get('name')
            SLA_time = request_body.get('SLA_time')
            process_time = request_body.get('process_time')
            department = request_body.get('department')
            escalate_time = request_body.get('escalate_time')

            SLA_time = int(SLA_time) * 60  # SLa time (seconds)
            process_time = int(process_time) * 60  # process time (seconds)

            if (SLA_time and department and SLA_name and process_time) is not None:

                while SLA_time >= 0:
                    SLA_time = SLA_time - 1
                    process_time = process_time + 1
                    time.sleep(1)
                    print('SLA name: ', SLA_name)
                    print('SLA time: ', SLA_time)
                    print('process time: ', process_time)
                    if 0 < SLA_time <= escalate_time:
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
                    print('SLA name: ', SLA_name)
                    print('SLA time: ', SLA_time)
                    print('process time: ', process_time)
                    if ticket_status == 'done':
                        return JsonResponse({
                            'message': 'done'
                        },status=status.HTTP_200_OK)
            else:
                return JsonResponse({
                    'message': 'Oop! Missing something, please check your input again.'
                }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as err:
        print('error', err)


def HmstoSeconds(string):
    string = str(string)
    stringH = float(string.split(":")[0]) * 3600
    stringM = float(string.split(":")[1]) * 60
    stringS = float(string.split(":")[2])
    string = stringH + stringM + stringS  # string(seconds)
    return string


@csrf_exempt
# http://localhost:8000/api/checktime/
def check_created_time(request):
    try:
        if request.method == 'POST':
            request_body = json.loads(request.body)
            print("data: ", request_body)
            working_time = request_body.get('working_time')
            created_time = request_body.get('created_time')
            created_time = str(created_time.split(" ")[1])

            SLA_time = request_body.get('SLA_time')
            # SLA_timeH = int(SLA_time.split(":")[0]) * 3600
            # SLA_timeM = int(SLA_time.split(":")[1]) * 60
            # SLA_timeS = int(SLA_time.split(":")[2])
            # SLA_time = SLA_timeH + SLA_timeM + SLA_timeS
            SLA_time = HmstoSeconds(SLA_time)  # SLA_time(seconds)
            print('SLA_time', SLA_time)
            print(type(SLA_time))

            department = request_body.get('department')
            process_time = request_body.get('process_time')

            escalate_time = request_body.get('escalate_time')
            # escalate_timeH = int(escalate_time.split(":")[0]) * 3600
            # escalate_timeM = int(escalate_time.split(":")[1]) * 60
            # escalate_timeS = int(escalate_time.split(":")[2])
            # escalate_time = escalate_timeH + escalate_timeM + escalate_timeS
            escalate_time = HmstoSeconds(escalate_time)  # escalate_time(seconds)
            print('escalate_time', escalate_time)
            print(type(escalate_time))

            thread_id = 0
            # Xử lý thời gian làm việc của một công ty (working time) để so sánh với created_time:
            # Nếu working time == weekly time (work 24/7) thì created_time là bất kỳ và SLA_time bắt đầu được đếm ngược.
            # Nếu working time == business time (sẽ cho user setting start_time va end_time --> get được 2 values này)
            # thì sẽ so sánh:
            # - start_time <= created_time < end_time --> SLA_time bắt đầu được đếm ngược.
            # - ngược lại thì SLA_time sẽ dừng đến khi điều kiện trên được thỏa.
            # - trường hợp created_time < end_time nhưng thời gian ko còn đủ cho SLA_time đếm ngược
            # thì lúc này sẽ tính toán thời gian còn lại == end_time - created_time và SLA_time sẽ đếm tới đó thì dừng
            # chuyển sang start_time của ngày tiếp theo thì SLA_time sẽ tiếp tục đếm ngược

            if working_time == 'weekly time':
                # Run async SLA time
                thread1 = threading.Thread(target=timer, args=(request, SLA_time, process_time, department, escalate_time))
                thread1.setDaemon(True)
                thread1.start()
                thread_id = threading.get_ident()
                # thread1.is_alive()
                thread1.join()
            elif working_time == 'business time':
                start_time = request_body.get('start_time')
                end_time = request_body.get('end_time')

                # start_timeH = int(start_time.split(":")[0]) * 3600
                # start_timeM = int(start_time.split(":")[1]) * 60
                # start_timeS = int(start_time.split(":")[2])
                # start_time = start_timeH + start_timeM + start_timeS
                start_time = HmstoSeconds(start_time)  # start_time(seconds)
                print('start_time', start_time)
                print(type(start_time))

                # end_timeH = int(end_time.split(":")[0]) * 3600
                # end_timeM = int(end_time.split(":")[1]) * 60
                # end_timeS = int(end_time.split(":")[2])
                # end_time = end_timeH + end_timeM + end_timeS
                end_time = HmstoSeconds(end_time)  # end_time(seconds)
                print('end_time', end_time)
                print(type(end_time))

                # created_timeH = int(created_time.split(":")[0]) * 3600
                # created_timeM = int(created_time.split(":")[1]) * 60
                # created_timeS = int(created_time.split(":")[2])
                # created_time = created_timeH + created_timeM + created_timeS
                created_time = HmstoSeconds(created_time)  # created_time(seconds)
                print('created_time', created_time)
                print(type(created_time))

                BaseTime = '24:00:00'
                # BaseTimeH = int(BaseTime.split(":")[0]) * 3600
                # BaseTimeM = int(BaseTime.split(":")[1]) * 60
                # BaseTimeS = int(BaseTime.split(":")[2])
                # BaseTime = BaseTimeH + BaseTimeM + BaseTimeS
                BaseTime = HmstoSeconds(BaseTime)  # BaseTime(seconds)
                print('BaseTime', BaseTime)
                print(type(BaseTime))

                if start_time <= created_time < end_time:
                    if SLA_time <= (end_time - created_time):
                        # Run async SLA time
                        thread1 = threading.Thread(target=timer, args=(request, SLA_time, process_time, department, escalate_time))
                        thread1.setDaemon(True)
                        thread1.start()
                        thread_id = threading.get_ident()
                        # thread1.is_alive()
                        thread1.join()
                        data = {
                            'created_time': created_time,
                            'SLA_time': SLA_time,
                            'escalate_time': escalate_time,
                            'thread_id': thread_id,
                        }
                        return JsonResponse({
                            'data': data
                        }, status=status.HTTP_200_OK)
                    else:
                        SLA_time = SLA_time + ((BaseTime - end_time) + start_time)
                        print('SLA_time_plus', SLA_time)
                        escalate_time = escalate_time + ((BaseTime - end_time) + start_time)
                        print('escalate_time_plus', escalate_time)
                        # Run async SLA time
                        thread1 = threading.Thread(target=timer, args=(request, SLA_time, process_time, department, escalate_time))
                        thread1.setDaemon(True)
                        thread1.start()
                        thread_id = threading.get_ident()
                        # thread1.is_alive()
                        thread1.join()
                        data = {
                            'created_time': created_time,
                            'SLA_time': SLA_time,
                            'escalate_time': escalate_time,
                            'thread_id': thread_id,
                        }
                        return JsonResponse({
                            'data': data
                        }, status=status.HTTP_200_OK)
                else:
                    print("Full time, please return at the next day!")
                    return JsonResponse({
                        'message': 'Oop!Full time, please return at the next day!'
                    }, status=status.HTTP_200_OK)

            # data = {
            #     'created_time': created_time,
            #     'SLA_time': SLA_time,
            #     'escalate_time': escalate_time,
            #     'thread_id': thread_id,
            # }
            # return JsonResponse({
            #     'data': data
            # },status=status.HTTP_200_OK)
    except Exception as err:
        print("error: ", err)


@csrf_exempt
# http://localhost:8000/api/reset/
def database_reset(request):
    try:
        if request.method == 'POST':
            request_body = json.loads(request.body)
            ticket_status = request_body.get('status')
            process_time = request_body.get('process_time')
            response_time = request_body.get('response_time')
            SLA_name = request_body.get('name')
            department = request_body.get('department')
            result = request_body.get('result')
            get_data = col.find({'name': SLA_name, 'department': department})
            print('request_body', request_body)
            print('get_data', get_data[0])
            print('status', get_data[0]['status'])
            print('process_time', get_data[0]['process_time'])
            print('response_time', get_data[0]['response_time'])
            print('result', get_data[0]['result'])

            data = {
                "SLA_name": SLA_name,
                "department": department,
                "status": get_data[0]['status'],
                "process_time": get_data[0]['process_time'],
                "response_time": get_data[0]['response_time'],
                "result": get_data[0]['result']
            }
            data1 = {
                "$set": {
                    "status": ticket_status,
                    "process_time": process_time,
                    "response_time": response_time,
                    "result": result
                }
            }
            new = col.update_one(data, data1)
            print('modified', new.modified_count)
            return JsonResponse({
                'message': 'update one element successful.'
            },status=status.HTTP_201_CREATED)

    except Exception as err:
        print("error: ", err)
