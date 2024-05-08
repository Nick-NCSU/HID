#!/usr/bin/env python3
from functools import reduce
import json
from operator import concat
from flask import Flask, request

LOWER_SYMBOL_MAP = json.loads(open('data/lower.json').read())
UPPER_SYMBOL_MAP = json.loads(open('data/upper.json').read())

def print_hid(modifiers, keys):
    print(keys)
    data = chr(get_modifier_byte(modifiers)) + chr(0) + reduce(concat, [chr(int(get_key_byte(key), 16)) for key in keys])
    with open('/dev/hidg0', 'rb+') as fd:
        fd.write(data.encode())

def get_modifier_byte(modifiers):
    bitmap = [
        'left_ctrl',
        'left_shift',
        'left_alt',
        'left_gui',
        'right_ctrl',
        'right_shift',
        'right_alt',
        'right_gui'
    ]
    return reduce(lambda x, y: x | y, [0b00000001 << i if modifiers.get(bitmap[i], False) else 0 for i in range(len(bitmap))])

def get_key_byte(key):
    return LOWER_SYMBOL_MAP.get(key, False) or UPPER_SYMBOL_MAP.get(key, '0x00')

app = Flask(__name__)

# Send a null keypress to reset the keyboard
#
# This can be used to reset the keyboard if it gets stuck
# by rebooting the device
print_hid({}, [chr(0)] * 6) 

@app.route('/keys', methods=['POST'])
def keys():
    modifiers = request.json.get('modifiers', {})
    keys = request.json.get('keys', [])
    if len(keys) < 6:
        keys = keys + [chr(0)] * (6 - len(keys))
    elif len(keys) > 6:
        keys = keys[:6]
    print_hid(modifiers, keys)
    return 'OK'

@app.route('/')
def health_check():
    return 'OK'