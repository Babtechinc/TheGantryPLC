import json
import time
from pymodbus.client import ModbusTcpClient

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

def main():
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
    print(client.read_holding_registers(11).registers)
    print(result)
    while True:
        result = read_modbus_coils(client, 1)[0]
        if result:
            write_modbus_coils(client, 10, True)
            write_modbus_coils(client, 5, True)
            time.sleep(1)
            write_modbus_coils(client, 5, False)
            time.sleep(1)
            write_modbus_coils(client, 18, True)
            time.sleep(5)
            write_modbus_coils(client, 18, False)
            time.sleep(1)
            write_modbus_coils(client, 5, True)
            time.sleep(1)
        
        # print(result)
        # time.sleep(1)










if __name__ == '__main__':
    main()
