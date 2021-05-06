import json
import logging
import time

import obd
from loguru import logger

from guglhupf.core.settings import settings

CONNECTION = obd.Async(settings.obd_device)
COMMANDS = {
    # (Vehicle Speed; Unit.kph -> Unit.mph)
    obd.commands.SPEED: {
        'conv': lambda obd_val: obd_val.to('mph').magnitude,
        'id': 'SPEED',
        'label': 'Speed',
        'unit': 'mph',
    },
    # (Engine RPM; Unit.rpm)
    obd.commands.RPM: {
        'conv': lambda obd_val: obd_val.magnitude,
        'id': 'RPM',
        'label': 'rpm',
        'unit': 'rpm',
    },
    # (Throttle Position; Unit.percent)
    obd.commands.THROTTLE_POS: {
        'conv': lambda obd_val: obd_val.magnitude,
        'id': 'THROTTLE',
        'label': 'Throttle',
        'unit': '%',
    },
    # (Calculated Engine Load; Unit.percent)
    obd.commands.ENGINE_LOAD: {
        'conv': lambda obd_val: obd_val.magnitude,
        'id': 'LOAD',
        'label': 'Engine Load',
        'unit': '%',
    },
    # (Fuel Level Input; Unit.percent)
    obd.commands.FUEL_LEVEL: {
        'conv': lambda obd_val: obd_val.magnitude,
        'id': 'FUEL',
        'label': 'Fuel Level',
        'unit': '%',
    },
    # (Engine oil temperature; Unit.celsius -> Unit.fahrenheit)
    obd.commands.OIL_TEMP: {
        'conv': lambda obd_val: obd_val.to('degF').magnitude,
        'id': 'OIL',
        'label': 'Oil',
        'unit': '°F',
    },
    # (Engine coolant temperature; Unit.celsius -> Unit.fahrenheit)
    obd.commands.COOLANT_TEMP: {
        'conv': lambda obd_val: obd_val.to('degF').magnitude,
        'id': 'COOLANT',
        'label': 'Coolant',
        'unit': '°F',
    },
    # (Intake air temperature; Unit.celsius -> Unit.fahrenheit)
    obd.commands.INTAKE_TEMP: {
        'conv': lambda obd_val: obd_val.to('degF').magnitude,
        'id': 'INTAKE',
        'label': 'Intake',
        'unit': '°F',
    },
    # (Ambient air temperature; Unit.celsius -> Unit.fahrenheit)
    obd.commands.AMBIANT_AIR_TEMP: {
        'conv': lambda obd_val: obd_val.to('degF').magnitude,
        'id': 'OUTSIDE',
        'label': 'Outside',
        'unit': '°F',
    },
}


def query(command):
    response = CONNECTION.query(command)
    return None if response.is_null() else COMMANDS[command]['conv'](
        response.value,
    )


def start():
    for command in COMMANDS.keys():
        CONNECTION.watch(command)
    CONNECTION.start()  # start the async update loop


def all_stats():
    return {
        instructions['id']: {
            'value': query(command),
            'unit': instructions['unit'],
            'label': instructions['label'],
        }
        for command, instructions in COMMANDS.items()
    }


if __name__ == '__main__':
    start()
    for _ in range(5):
        logger.info(json.dumps(all_stats(), indent=4, sort_keys=True))
        time.sleep(1)
