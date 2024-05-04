import datetime
import os
import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.conf import settings
from multi_axis_robot import utils, models
from scada.Other.Utils import connect_to_plc


def control_mode(request):

    return render(
                    request,
                    "multi_axis_robot/control_mode.html",
                    {
                    }
    )


def data_table(request):
    # This was our old way of doing things.
    # It had issues as if we were writing to the cached JSON

    '''
    json_data_path = os.path.join(settings.BASE_DIR, "Extras/multi_axis_robot.json")
    data = utils.read_json_file(json_data_path)
    '''

    # Get the latest timestamp out of the database 
    latest_timestamp = models.MultiAxisDataPoint.objects.order_by('-timestamp').first()

    recent_data_points = models.MultiAxisDataPoint.objects.filter(timestamp=latest_timestamp.timestamp)

    return render(
                    request,
                    "multi_axis_robot/data_table.html",
                    {
                        'data': recent_data_points,
                    }
    )


def graph(request):
    # Predefine our lists for graphing
    value_list = []
    timestamp_list = []
    tag_name = None

    # Query the step motor DP table for distinct (unique) values in the tag_name field
    tag_names = models.MultiAxisDataPoint.objects.values_list('tag_name').distinct()

    # Cast our queryset to a list of tuples as its easier to deal with
    tag_names = list(tag_names)
    # Covert out queryset list of tuples to a single list of the tag names
    tag_names = list(sum(tag_names, ()))


    if request.method=="POST":
        tag_name = request.POST['tag_name']
        data = models.MultiAxisDataPoint.objects.filter(tag_name=tag_name).order_by('timestamp')
    
        for data_point in data:
            value_list.append(data_point.tag_value)
            timestamp_list.append(data_point.timestamp.strftime("%m/%d/%Y, %H:%M:%S"))


    return render(
                    request,
                    "multi_axis_robot/graph.html",
                    {
                        'chosen_tag': tag_name,
                        'tag_options': tag_names,
                        'values': value_list,
                        'timestamps': timestamp_list,
                    }
    )


@csrf_exempt
def receive_stepper_data(request):
    if request.method=='POST':
        # Take our received JSON data and load that into python dictionary
        data_dict =json.loads(request.body)
        # If our data is not empty
        if data_dict:
            utils.save_data(data_dict)
            # Return success response code
            return HttpResponse(status=200)
        # if empty return no data response code
        else:
            # Return no content response code
            return HttpResponse(status=204)

@csrf_exempt
def receive_write_to_plc(request):
    if request.method=='POST':
        # Take our received JSON data and load that into python dictionary
        print(request.body)
        print(request.POST)
        data_dict = {}
        # data_dict =json.loads(request.body)
        # If our data is not empty
        if data_dict:
            utils.save_data(data_dict)
            # Return success response code
            return HttpResponse(status=200)
        # if empty return no data response code
        else:
            # Return no content response code
            return HttpResponse(status=204)
@csrf_exempt
def write_to_plc_program(request):
    if request.method=='POST':
        # Take our received JSON data and load that into python dictionary
        print(request.body)
        print(request.POST)
        data_dict = {}

        client = connect_to_plc()
        reg = client.write_register(11, 2000)
        # print(reg)
        print(client.read_holding_registers(11).registers)

        # data_dict =json.loads(request.body)
        # If our data is not empty
        if data_dict:
            utils.save_data(data_dict)
            # Return success response code
            return HttpResponse(status=200)
        # if empty return no data response code
        else:
            # Return no content response code
            return HttpResponse(status=204)
