#!/usr/bin/env python3

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import json, time, util

system_status_map = {
    0: 'Standby',
    1: '(No Use)',
    2: 'Discharge',
    3: 'Fault',
    4: 'Flash',
    5: 'PV charge',
    6: 'AC charge',
    7: 'Combine charge',
    8: 'Combine charge and Bypass',
    9: 'PV charge and Bypass',
    10: 'AC charge and Bypass',
    11: 'Bypass',
    12: 'PV charge and Discharge'
}

check_step_map = {
    1: 'PV1 charge power check',
    2: 'PV2 charge power check',
    3: 'AC charge Power check'
}

production_line_mode_map = {
    0: 'Not at Production Line Mode',
    1: 'Production Line Mode',
    2: 'Production Line Clear Fault Mode'
}

constant_power_ok_flag_map = {
    0: 'Not OK',
    1: 'OK'
}

bat_over_charge_map = {
    0: 'Battery not over charge',
    1: 'Battery over charge'
}

parameters = {
        'ac_charger_amps': { 'low_register': 68, 'description': 'AC Charge Battery Current', 'unit': 'A', 'multiplier': .1 },
        'ac_charger_kwh_today': { 'high_register': 56, 'low_register': 57, 'description': 'AC charge Energy today', 'unit': 'KWH', 'multiplier': .1 },
        'ac_charger_kwh_total': { 'high_register': 58, 'low_register': 59, 'description': 'AC charge Energy total', 'unit': 'KWH', 'multiplier': .1 },
        'ac_charger_voltamps': { 'high_register': 15, 'low_register': 16, 'description': 'AC charge apparent power', 'unit': 'VA', 'multiplier': .1 },
        'ac_charger_watts': { 'high_register': 13, 'low_register': 14, 'description': 'AC charge watt', 'unit': 'W', 'multiplier': .1 },
        'ac_discharge_kwh_today': { 'high_register': 64, 'low_register': 65, 'description': 'AC discharge Energy today', 'unit': 'KWH', 'multiplier': .1 },
        'ac_discharge_kwh_total': { 'high_register': 66, 'low_register': 67, 'description': 'AC discharge Energy total', 'unit': 'KWH', 'multiplier': .1 },
        'ac_discharge_voltamps': { 'high_register': 71, 'low_register': 72, 'description': 'AC discharge apparent power', 'unit': 'VA', 'multiplier': .1 },
        'ac_discharge_watts': { 'high_register': 69, 'low_register': 70, 'description': 'AC discharge watt', 'unit': 'W', 'multiplier': .1 },
        'ac_input_frequency': { 'low_register': 21, 'description': 'AC input frequency', 'unit': 'Hz', 'multiplier': .01 },
        'ac_input_voltage': { 'low_register': 20, 'description': 'AC input Volt', 'unit': 'V', 'multiplier': .1 },
        'ac_input_voltamps': { 'high_register': 38, 'low_register': 39, 'description': 'AC input apparent power', 'unit': 'VA', 'multiplier': .1 },
        'ac_input_watts': { 'high_register': 36, 'low_register': 37, 'description': 'AC input watt', 'unit': 'W', 'multiplier': .1 },
        'ac_output_amps': { 'low_register': 34, 'description': 'Output Current', 'unit': 'A', 'multiplier': .1 },
        'ac_output_frequency': { 'low_register': 23, 'description': 'AC output frequency', 'unit': 'Hz', 'multiplier': .01 },
        'ac_output_voltage': { 'low_register': 22, 'description': 'AC output Volt', 'unit': 'V', 'multiplier': .1 },
        'battery_discharge_kwh_today': { 'high_register': 60, 'low_register': 61, 'description': 'Bat discharge Energy today', 'unit': 'KWH', 'multiplier': .1 },
        'battery_discharge_kwh_total': { 'high_register': 62, 'low_register': 63, 'description': 'Bat discharge Energy total', 'unit': 'KWH', 'multiplier': .1 },
        'battery_discharge_voltamps': { 'high_register': 75, 'low_register': 76, 'description': 'Bat discharge apparent power', 'unit': 'VA', 'multiplier': .1 },
        'battery_discharge_watts': { 'high_register': 73, 'low_register': 74, 'description': 'Bat discharge watt', 'unit': 'W', 'multiplier': .1 },
        'battery_over_charge': { 'low_register': 80, 'description': 'Battery Over Charge Flag', 'mapping': bat_over_charge_map },
        'battery_state_of_charge': { 'low_register': 18, 'description': 'Battery SOC', 'unit': '%' },
        'battery_voltage': { 'low_register': 17, 'description': 'Battery volt (M3)', 'unit': 'V', 'multiplier': .01 },
        'battery_watts': { 'high_register': 77, 'low_register': 78, 'description': 'Bat watt', 'unit': 'W', 'multiplier': .1, 'signed': True },
        'bus_voltage': { 'low_register': 19, 'description': 'Bus Voltage', 'unit': 'V', 'multiplier': .1 },
        'check_step': { 'low_register': 45, 'description': 'Product check step', 'mapping': check_step_map },
        'constant_power_ok': { 'low_register': 47, 'description': 'Constant Power OK Flag', 'mapping': constant_power_ok_flag_map },
        'dc_output_voltage': { 'low_register': 24, 'description': 'Output DC Volt', 'unit': 'V', 'multiplier': .1 },
        'dcdc_temperature': { 'low_register': 26, 'description': 'DC‐DC Temperature', 'unit': 'C', 'multiplier': .1 },
        'dtc': { 'low_register': 44, 'description': 'Device Type Code' },
        'fault_bit': { 'low_register': 40, 'description': 'fault bit' },
        'fault_value': { 'low_register': 42, 'description': 'fault value' },
        'inverter_amps': { 'low_register': 35, 'description': 'Inv Current', 'unit': 'A', 'multiplier': .1 },
        'inverter_fan_speed': { 'low_register': 82, 'description': 'Fan speed of Inverter', 'unit': '%' },
        'inverter_temperature': { 'low_register': 25, 'description': 'Inv Temperature', 'unit': 'C', 'multiplier': .1 },
        'load_percentage': { 'low_register': 27, 'description': 'Load Percent', 'unit': '%', 'multiplier': .1 },
        'output_voltamps': { 'high_register': 11, 'low_register': 12, 'description': 'Output apparent power', 'unit': 'VA', 'multiplier': .1 },
        'output_watts': { 'high_register': 9, 'low_register': 10, 'description': 'Output active power', 'unit': 'W', 'multiplier': .1 },
        'production_line_mode': { 'low_register': 46, 'description': 'Production Line Mode', 'mapping': production_line_mode_map },
        'solar_charger_fan_speed': { 'low_register': 81, 'description': 'Fan speed of MPPT Charger', 'unit': '%' },
        'solar_charger_watts': { 'high_register': 3, 'low_register': 4, 'description': 'PV1 charge power', 'unit': 'W', 'multiplier': .1 },
        'solar_kwh_today': { 'high_register': 48, 'low_register': 49, 'description': 'PV1 Energy today', 'unit': 'KWH', 'multiplier': .1 },
        'solar_kwh_total': { 'high_register': 50, 'low_register': 51, 'description': 'PV1 Energy total', 'unit': 'KWH', 'multiplier': .1 },
        'solar_voltage': { 'low_register': 1, 'description': 'PV1 voltage', 'unit': 'V', 'multiplier': .1 },
        'status': { 'low_register': 0, 'description': 'System run state', 'mapping': system_status_map },
        'warning_bit': { 'low_register': 41, 'description': 'Warning bit' },
        'warning_value': { 'low_register': 43, 'description': 'warning value' },
        'work_time_total': { 'high_register': 30, 'low_register': 31, 'description': 'Work time total', 'unit': 'S', 'multiplier': .5 }
}

registers = []

def get_power(verbose):
    read_inverter()
    power = {}
    for key, metadata in parameters.items():
        power[key] = param(metadata, verbose)
    return power
    
def read_inverter():
    global registers
    # Read data from inverter
    inverter = ModbusClient(method='rtu', port='/dev/ttyUSB0', baudrate=9600, stopbits=1, parity='N', bytesize=8, timeout=1)
    inverter.connect()
    rr1 = inverter.read_input_registers(0,45)
    while (isinstance(rr1, Exception)):
        print(rr1)
        rr1 = inverter.read_input_registers(0,45)
    rr2 = inverter.read_input_registers(45,45)
    while (isinstance(rr2, Exception)):
        print(rr2)
        rr2 = inverter.read_input_registers(45,45)
    inverter.close()
    registers = rr1.registers + rr2.registers

def param(metadata, verbose):
    value = registers[metadata['low_register']]

    if 'high_register' in metadata:
        value += registers[metadata['high_register']] << 16
    if 'signed' in metadata and metadata['signed'] == True:
        value = int.from_bytes(value.to_bytes(4, byteorder='big', signed=False), byteorder='big', signed=True)
    if 'multiplier' in metadata:
        value = round(float(value)*metadata['multiplier'], 2)
    if 'mapping' in metadata:
        value = metadata['mapping'][value]
    response = {
        'value': value,
        'label': metadata['description']
    }
    if 'unit' in metadata:
        response['unit'] = metadata['unit']
        if response['unit'] == 'C':
            response['value'] = util.celsius_to_fahrenheit(response['value'])
            response['unit'] = 'F'
    if verbose:
        return response
    else:
        return response['value']

if __name__ == '__main__':
    while True:
        power = get_power(False)
        with open('../data/power.json', 'w') as f:
            f.write(json.dumps(power))
        time.sleep(5)

