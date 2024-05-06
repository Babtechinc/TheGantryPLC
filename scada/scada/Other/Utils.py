from pymodbus.client import ModbusTcpClient


def connect_to_plc():
    client = ModbusTcpClient('192.168.2.23', port="502")
    client.connect()
    return client


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

def close_connection_to_click(client):
    client.close()
