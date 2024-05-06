import datetime
import os
import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.conf import settings
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder
import time
import math
from multi_axis_robot import utils, models
from scada.Other.Utils import connect_to_plc,read_modbus_coils,write_modbus_coils

def interpretation_value(value):
    if value > 32767:  # Check if the value is negative
        value = value - 65536  # Convert to negative representation
    return abs(value)
def control_mode(request):
    data = {
                    }
    try:
    
        client = connect_to_plc()
        inputSpeedOfStepperx =  client.read_holding_registers(11).registers[0]
        inputSpeedOfStepperz = client.read_holding_registers(12).registers[0]
        turnOnMotor = read_modbus_coils(client, 18)[0]
        
        data={
            "inputSpeedOfStepperx": interpretation_value( inputSpeedOfStepperx),
            "inputSpeedOfStepperz": interpretation_value(inputSpeedOfStepperz),
            "DirectionOfStepperX":'0' if inputSpeedOfStepperx > 32767 else '1',
            "DirectionOfStepperZ":'0' if inputSpeedOfStepperz > 32767 else '1',
            "turnOnMotor":'0' if not turnOnMotor else '1',
        }
    except:
        print("No Connection ")

    return render(
                    request,
                    "multi_axis_robot/control_mode.html",
                    data
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
        client = connect_to_plc()

        print(client.read_holding_registers(11).registers)
        
        switch = read_modbus_coils(client, 1)[0]
        write_modbus_coils(client, 10, True)
        if not switch:
            return HttpResponse(status=200)
        if 'turnOnMotor' in request.POST:
            turnOnMotor = int(request.POST['turnOnMotor'])
            if turnOnMotor == 1:
                write_modbus_coils(client, 5, False)
                time.sleep(1)
                write_modbus_coils(client, 18, True)

            else:
                write_modbus_coils(client, 18, False)
                time.sleep(1)
                write_modbus_coils(client, 5, True)
                return HttpResponse(status=200)
            
        if 'inputSpeedOfStepperx' in request.POST:
            inputSpeedOfStepperx = abs( int(request.POST['inputSpeedOfStepperx']))
            if 'DirectionOfStepperX' in request.POST:
                
                
                DirectionOfStepperX = request.POST['DirectionOfStepperX']
                if DirectionOfStepperX =='0':
                    
                    print("heleo")

                    inputSpeedOfStepperx= -1 * inputSpeedOfStepperx
                    builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
                    builder.add_16bit_int(inputSpeedOfStepperx)
                    payload = builder.build()

                    client.write_registers(10 + 1, payload, skip_encode=True, unit=1)
                else:

                    reg = client.write_register(10+1,inputSpeedOfStepperx)
        if 'inputSpeedOfStepperz' in request.POST:
            inputSpeedOfStepperz = abs(int(request.POST['inputSpeedOfStepperz']))

            if 'DirectionOfStepperZ' in request.POST:
                DirectionOfStepperZ = request.POST['DirectionOfStepperZ']
                if DirectionOfStepperZ =='0':
                    print("hele")
                    inputSpeedOfStepperz= -1 * inputSpeedOfStepperz
                    builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
                    builder.add_16bit_int(inputSpeedOfStepperz)
                    payload = builder.build()
                    client.write_registers(11 + 1, payload, skip_encode=True, unit=1)
                else:
                    reg = client.write_register(11+1,inputSpeedOfStepperz)
        write_modbus_coils(client, 18, False)
        time.sleep(1)
        write_modbus_coils(client, 5, True)
        time.sleep(1)
        write_modbus_coils(client, 5, False)
        time.sleep(1)
        write_modbus_coils(client, 18, True)

        
    
        return HttpResponse(status=200)
        # if empty return no data response code
        
@csrf_exempt
def write_to_plc_program(request):
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
