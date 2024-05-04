from pymodbus.client import ModbusTcpClient


def connect_to_plc():
    client = ModbusTcpClient('192.168.2.23', port="502")
    client.connect()
    return client


def read_coils(client, coil_number, number_of_coils=1):
    # Address the offset coil
    coil_number = coil_number - 1
    result = client.read_coils(coil_number, number_of_coils)
    result_list = result.bits[0:number_of_coils]
    return result_list


def write_modbus_coil(client, coil_number, value):
    coil_number = coil_number - 1
    result = client.write_coils(coil_number, value)


def close_connection_to_click(client):
    client.close()
