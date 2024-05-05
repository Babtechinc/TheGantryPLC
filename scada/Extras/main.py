from datetime import datetime
import json
import time
from pymodbus.client import ModbusTcpClient
import requests

# Advanced PLCs Python Code from 03/19/2024
# This code is written in the Pep 8 styling guide
# and is checked via pycodestyle

click_ip_address = '192.168.2.23'


class PLCTag():
    def __init__(self, name, modbus_address, value):
        self.name = name
        self.modbus_address = modbus_address
        self.value = value


def write_modbus_coils(client, coil_address, value):

    result = None
    # Take care of the offset between pymodbus and the click plc
    coil_address = coil_address - 1

    # pymodbus built in write coil function
    result = client.write_coil(coil_address, value)

    return result


def read_modbus_coils(client, coil_address, number_of_coils=1):
    # Predefining a empty list to store our result
    result_list = []

    # Take care of the offset between pymodbus and the click plc
    coil_address = coil_address - 1

    # Read the modbus address values form the click PLC
    result = client.read_coils(coil_address, number_of_coils)

    # print("Response from PLC with pymodbus library", result.bits)

    # storing our values form the plc in a list of length
    # 0 to the number of coils we want to read
    result_list = result.bits[0:number_of_coils]

    # print("Filtered result of only necessary values", result_list)
    return result_list


def pulse_stepper_motor(client, stepper_motor_pulse):
    # Create Motor Pulse Object
    # Turn on stepper motor pulse coil 16390
    # wait for a certain amount of time
    # Turn off stepper motor pulse coil 16390
    # wait for a certain amount of time
    write_modbus_coils(
            client,
            stepper_motor_pulse.modbus_address,
            stepper_motor_pulse.value
        )


def connect_to_click_plc():
    # Attempting to create connection to click PLC
    # Return client object for other functions

    print("Attempting to connect to PLC")

    # Creating a client object with the parameters of the PLC IP and Port
    click_plc_obj = ModbusTcpClient(click_ip_address, port='502')

    # Attempt to connect to the PLC
    click_plc_obj.connect()
    print("connected to PLC")

    # Return our PLC object
    return click_plc_obj


def disconnect_from_click_plc(client):
    print("Disconnecting from click PLC")
    client.close()

def write_to_json_file(filename, data_dict):
    with open(filename, "w") as file:
        json.dump(data_dict, file)

def create_data_structure_for_cache(*args):
    # Creating tag dictionary
    # IE: {'In hand': True, "In auto": False}

    result_dict = {}
    # Iterate through unknown number of objects
    for argument in args:
        result_dict[argument.name] = argument.value

    # Append a timestamp 
    now = datetime.now()
    result_dict["timestamp"] = now.strftime("%m/%d/%Y, %H:%M:%S")

    # Result dict = {"In Hand": True, ...., "timestamp": "04/24/2024, 3:37:15"}
    return result_dict

def send_data_to_webserver(data_dict, session):
    # Convert from python dict to JSON string
    # to be able to send to our django web server
    json_string = json.dumps(data_dict)

    # This is the site you are trying to send to
    site_url = 'http://localhost:8000/receive-stepper-data/'
    # These are some headers for your browser, I wouldn't worry about these
    headers = {'User-Agent': 'Mozilla/5.0'}

    # This is sending the data to the webserver
    r = session.post(site_url, data=json_string, headers=headers)

    # This is the webservers response, which if it is working
    # should be a response code of 200
    print(r.status_code)

def main():
    tag_dict = {}
    
    # Create a session with our webserver to speed things up
    session = requests.Session()
    # Create client object for the click PLC
    # and connect to the PLC
    client = connect_to_click_plc()
    print("Initialize Axis")
    # print("Turn off enable")
    # write_modbus_coils(client, 5, False)
    # time.sleep(1)
    # write_modbus_coils(client, 18, True)
    # time.sleep(5)
    # write_modbus_coils(client, 18, False)
    # time.sleep(1)
    # write_modbus_coils(client, 5, True)
    result = read_modbus_coils(client, 1)[0]
    reg = client.write_register(11, 2000)
    # print(reg)
    # print(client.read_holding_registers(11).registers)
    # print(result)

     # Create our objects for each PLC tag
    sm_yellow_z_pos = PLCTag("Yellow SM Positon", 1, None)
    sm_yellow_z_vel = PLCTag("Yellow SM Velocity", 2, None)
    sm_blue_z_pos = PLCTag("Blue SM Positon", 1, None)
    sm_blue_z_vel = PLCTag("Blue SM Velocity", 1, None)
    sm_red_x_pos = PLCTag("Red SM Positon", 1, None)
    sm_red_x_vel = PLCTag("Red SM Velocity", 1, None)

    write_modbus_coils(client, 10, True)
    write_modbus_coils(client, 5, True)
    time.sleep(1)
    write_modbus_coils(client, 5, False)

    while True:
        # print(client.read_holding_registers(0,6).registers)
        dist_data = client.read_holding_registers(0,6).registers
        sm_yellow_z_pos.value = dist_data[0]
        sm_yellow_z_vel.value = dist_data[1]
        sm_blue_z_pos.value = dist_data[2]
        sm_blue_z_vel.value = dist_data[3]
        sm_red_x_pos.value = dist_data[4]
        sm_red_x_vel.value = dist_data[5]
        result = read_modbus_coils(client, 1)[0]
        # write_modbus_coils(client, 10, True)
        # write_modbus_coils(client, 5, True)
        # time.sleep(1)
        # write_modbus_coils(client, 5, False)
        if result:
            # time.sleep(1)
            write_modbus_coils(client, 18, True)
            # time.sleep(5)
            # write_modbus_coils(client, 18, False)
            # time.sleep(1)
            # write_modbus_coils(client, 5, True)
            # time.sleep(1)
        # setup tag dictionary with unlimited arguments
        tag_dict = create_data_structure_for_cache(
                                            sm_yellow_z_pos,
                                            sm_yellow_z_vel,
                                            sm_blue_z_pos,
                                            sm_blue_z_vel,
                                            sm_red_x_pos,
                                            sm_red_x_vel,
                                            # in_hand,
                                            # e_stop,
                                            # motor_pulse_feedback,
                                            # motor_direction_feedback,
                                            # motor_pulse_control,
                                            # motor_direction_control
                                        )
        send_data_to_webserver(tag_dict, session)
        # print(result)
        # time.sleep(1)




if __name__ == '__main__':
    main()
