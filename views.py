from django.http import JsonResponse
import pymongo
import json
from bson import json_util, ObjectId
from datetime import datetime

from django.views.decorators.csrf import csrf_exempt
from pymongo import MongoClient
from rest_framework import status
import time

import threading
# from threading import Thread


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
        if request.method == 'POST':
            request_body = json.loads(request.body)
            working_time = request_body.get('working_time')
            created_time = request_body.get('created_time')
            SLA_name = request_body.get('name')
            SLA_time = request_body.get('SLA_time')
            start_time = request_body.get('start_time')
            end_time = request_body.get('end_time')
            department = request_body.get('department')
            ticket_status = request_body.get('status')
            response_time = request_body.get('response_time')
            escalate_time = request_body.get('escalate_time')
            process_time = request_body.get('process_time')
            result = request_body.get('result')

            data = {
                "working_time": working_time,
                "created_time": created_time,
                "response_time": response_time,
                "department": department,
                "name": SLA_name,
                "status": ticket_status,
                "result": result,
                "process_time": process_time,
                "SLA_time": SLA_time,
                "start_time": start_time,
                "end_time": end_time,
                "escalate_time": escalate_time,
            }
            col.insert_one(data)
            return JsonResponse({
                'data': 'Create new element successful.'
            }, status=status.HTTP_201_CREATED)
    except Exception as err:
        print("error:", err)
        return JsonResponse({
            'message': 'Create unsuccessful.'
        }, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
# http://localhost:8000/api/update
def update_data(request, result, SLA_time, process_time, response_time):
    try:
        if request.method == 'POST':
            request_body = json.loads(request.body)
            _id = request_body.get('_id')

            col.update_one({'_id': ObjectId(_id)}, {
                "$set": {
                    'SLA_time': str(SLA_time),
                    'response_time': str(response_time),
                    'process_time': str(process_time),
                    'status': 'done',
                    'result': result,
                },
            })

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
            print('SLA_time1', SLA_time)
            print(type(SLA_time))

            SLA_time = HmstoSeconds(SLA_time)  # SLA time (seconds)
            print('SLA_time2', SLA_time)
            print(type(SLA_time))
            process_time = HmstoSeconds(process_time)  # process time (seconds)
            print('process_time1', process_time)
            print(type(process_time))
            # Apply threading to runtime timer() and show_result()
            if ticket_status == 'new':
                timer_data = check_created_time(request)
            elif ticket_status == 'done':
                # run async function show_result
                thread2 = threading.Thread(target=show_result,
                                           args=(request, SLA_time, process_time, department, ticket_status))
                thread2.setDaemon(True)
                thread2.start()
                thread_id = threading.get_ident()
                # thread2.is_alive()
                thread2.join()
            return JsonResponse({
                'message': 'ok.'
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
            response_time = request_body.get('response_time')
            response_time = HmstoSeconds(response_time)  # response_time(seconds)

            SLA_time = HmstoSeconds(SLA_time)  # SLA time (seconds)
            print('SLA_time2', SLA_time)

            process_time = request_body.get('process_time')
            process_time = HmstoSeconds(process_time)  # process_time(seconds)
            print('process_time1', process_time)

            result = ''
            ticket_status = request_body.get('status')

            escalate_time = request_body.get('escalate_time')
            escalate_time = HmstoSeconds(escalate_time)  # escalate_time(seconds)
            print('escalate_time', escalate_time)

            if ticket_status == 'done':
                if (response_time and department and SLA_name and SLA_time) is not None:
                    if response_time < 0:
                        result = result + 'Overdue'
                        update_data(request, result, SLA_time, process_time, response_time)
                        print("SLA name: ", SLA_name)
                        print("mess: ", result)
                        return JsonResponse({
                            'result': result
                        },status=status.HTTP_200_OK)
                    else:
                        if 0 <= response_time <= escalate_time:
                            result = result + 'Done and Escalated'
                            update_data(request, result, SLA_time, process_time, response_time)
                            print("SLA name: ", SLA_name)
                            print("mess: ", result)
                            return JsonResponse({
                                'result': result
                            }, status=status.HTTP_200_OK)
                        else:
                            result = result + 'Done'
                            update_data(request, result, SLA_time, process_time, response_time)
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
            escalate_time = HmstoSeconds(escalate_time)

            SLA_time = HmstoSeconds(SLA_time)  # SLA time (seconds)
            process_time = HmstoSeconds(process_time)  # process time (seconds)

            if (SLA_time and department and SLA_name and process_time) is not None:

                while SLA_time >= 0:
                    SLA_time = SLA_time - 1
                    process_time = process_time + 1
                    time.sleep(1)
                    print('SLA name: ', SLA_name)
                    print('SLA time: ', SLA_time)
                    print('process time: ', process_time)
                    if 0 < SLA_time <= escalate_time:
                        data = {
                            'message': 'Need to escalate.'
                        }
                        print('data:', data)
                    continue
                # else:
                #     ticket_status = request_body.get('status')
                #     SLA_time = SLA_time - 1
                #     process_time = process_time + 1
                #     time.sleep(1)
                #     print('SLA name: ', SLA_name)
                #     print('SLA time: ', SLA_time)
                #     print('process time: ', process_time)
                #     if ticket_status == 'done':
                timer_data = {
                    'SLA_name': SLA_name,
                    'response_time': SLA_time,
                    'process_time': process_time
                }
                return timer_data
                # return JsonResponse({
                #     'timer_data': timer_data
                # },status=status.HTTP_200_OK)
            else:
                return JsonResponse({
                    'message': 'Oop! Missing something, please check your input again.'
                }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as err:
        print('error', err)


def HmstoSeconds(string):
    try:
        string = string
        stringH = int(int(string.split(":")[0]) * 3600)
        stringM = int(int(string.split(":")[1]) * 60)
        stringS = int(int(string.split(":")[2]))
        string = stringH + stringM + stringS  # string(seconds)
        return string
    except Exception as err:
        print('error: ', err)


@csrf_exempt
# http://localhost:8000/api/checktime/
def check_created_time(request):
    try:
        if request.method == 'POST':
            request_body = json.loads(request.body)
            print("data: ", request_body)
            working_time = request_body.get('working_time')
            created_time = request_body.get('created_time')
            created_time = created_time.split(" ")[1]
            created_time = HmstoSeconds(created_time)  # created_time(seconds)
            print('created_time', created_time)

            SLA_time = request_body.get('SLA_time')
            SLA_time = HmstoSeconds(SLA_time)  # SLA_time(seconds)
            print('SLA_time', SLA_time)

            department = request_body.get('department')
            process_time = request_body.get('process_time')
            process_time = HmstoSeconds(process_time)  # process_time(seconds)

            escalate_time = request_body.get('escalate_time')
            escalate_time = HmstoSeconds(escalate_time)  # escalate_time(seconds)
            print('escalate_time', escalate_time)

            thread_id = 0
            # Xử lý thời gian làm việc của một công ty (working time) để so sánh với created_time:
            # Nếu working time == weekly time (work 24/7) thì created_time là bất kỳ và SLA_time bắt đầu được đếm ngược.
            # Nếu working time == business time (sẽ cho user setting start_time va end_time --> get được 2 values này)
            # thì sẽ so sánh:
            # - start_time <= created_time < end_time --> SLA_time bắt đầu được đếm ngược.
            # - ngược lại thì SLA_time sẽ dừng đến khi điều kiện trên được thỏa.
            # - trường hợp created_time < end_time nhưng thời gian ko còn đủ cho SLA_time đếm ngược
            # Khi SLA time vẫn còn mà end_time đến thì timer() vẫn sẽ chạy đếm ngược
            # với SLA time và Escalate_time lúc này cộng dồn thời gian
            # từ end_time ngày hôm nay đến start_time của ngày tiếp theo để đảm bảo vẫn escalate đúng thời gian.

            if working_time == 'weekly time':
                # Run async SLA time
                thread1 = threading.Thread(target=timer,
                                           args=(request, SLA_time, process_time, department, escalate_time))
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
            elif working_time == 'business time':
                start_time = request_body.get('start_time')
                end_time = request_body.get('end_time')

                start_time = HmstoSeconds(start_time)  # start_time(seconds)
                print('start_time', start_time)

                end_time = HmstoSeconds(end_time)  # end_time(seconds)
                print('end_time', end_time)

                BaseTime = '24:00:00'

                BaseTime = HmstoSeconds(BaseTime)  # BaseTime(seconds)
                print('BaseTime', BaseTime)

                if start_time <= created_time < end_time:
                    if SLA_time <= (end_time - created_time):
                        # Run async SLA time
                        thread1 = threading.Thread(target=timer,
                                                   args=(request, SLA_time, process_time, department, escalate_time))
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
# http://localhost:8000/api/updateresult/
def update_result(request):
    try:
        if request.method == 'POST':
            request_body = json.loads(request.body)
            ticket_status = request_body.get('status')
            process_time = request_body.get('process_time')
            response_time = request_body.get('response_time')
            _id = request_body.get('_id')
            SLA_name = request_body.get('name')
            department = request_body.get('department')
            result = request_body.get('result')
            get_data = col.find({'_id': ObjectId(_id)})
            print('request_body', request_body)

            col.update_one({'_id': ObjectId(_id)}, {
                "$set": {
                    "status": ticket_status,
                    "process_time": process_time,
                    "response_time": response_time,
                    "result": result
                }
            })
            return JsonResponse({
                'message': "Ok"
            }, status=status.HTTP_201_CREATED)

    except Exception as err:
        print("error: ", err)


def update_all_data(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        _id = request_body.get('_id')
        working_time = request_body.get('working_time')
        created_time = request_body.get('created_time')
        SLA_name = request_body.get('name')
        SLA_time = request_body.get('SLA_time')
        start_time = request_body.get('start_time')
        end_time = request_body.get('end_time')
        department = request_body.get('department')
        ticket_status = request_body.get('status')
        response_time = request_body.get('response_time')
        escalate_time = request_body.get('escalate_time')
        process_time = request_body.get('process_time')
        result = request_body.get('result')

        col.update_one({'_id': ObjectId(_id)}, {
            "$set": {
                "working_time": working_time,
                "created_time": created_time,
                "response_time": SLA_name,
                "department": SLA_time,
                "name": start_time,
                "status": end_time,
                "result": department,
                "process_time": ticket_status,
                "SLA_time": response_time,
                "start_time": escalate_time,
                "end_time": process_time,
                "escalate_time": result,
            }
        })
        return JsonResponse({
            'message': "Update element successfully."
        }, status=status.HTTP_201_CREATED)


@csrf_exempt
# http://localhost:8000/api/resultbyID/
def get_data_byID(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        _id = request_body.get('_id')
        tmp_type = col.find({'_id': ObjectId(_id)})
        data = json.loads(json_util.dumps(tmp_type))
        return JsonResponse({
            'data': data
        }, status=status.HTTP_200_OK)


@csrf_exempt
# http://localhost:8000/api/deleteone/
def delete_one(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        _id = request_body.get('_id')
        col.delete_one({'_id': ObjectId(_id)})
    return JsonResponse({
        'message': 'Delete one element.'
    })


@csrf_exempt
# http://localhost:8000/api/deleteall/
def delete_all(request):
    if request.method == 'POST':
        col.delete_many({})
    return JsonResponse({
        'message': 'Delete all elements.'
    })
