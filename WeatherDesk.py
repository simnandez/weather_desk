#!/usr/bin/env python3
# coding: utf-8

# Copyright © 2016 Bharadwaj Raju <bharadwaj.raju777@gmail.com>
# All Rights Reserved.
# This file is part of WeatherDesk.
#
# WeatherDesk is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# WeatherDesk is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WeatherDesk (in the LICENSE file).
# If not, see <http://www.gnu.org/licenses/>.

import argparse
import datetime
import json
import os
import subprocess
import sys
import time
import traceback
import urllib.error
import urllib.parse

from itertools import product
from urllib.request import urlopen

import Desktop

import socket
REMOTE_SERVER = "www.google.com"

NAMING_RULES = '''
This is how to name files in the wallpaper directory:\n

       WEATHER		     |	FILENAME
_________________________|________________
 Clear, Calm, Fair:	     | normal{0}
 Thunderstorm:		     | thunder{0}
 Windy, Breeze, Gale:	 | wind{0}
 Drizzle, Rain, Showers: | rain{0}
 Snow:				     | snow{0}
 Cloudy:				 | cloudy{0}
 Other:				     | normal{0}

 If you use --no-weather, the files have to be named simply after the time of day depending of your time schema.
 E.g.: "day.jpg", "night.jpg"
'''


def get_args():
    arg_parser = argparse.ArgumentParser(
        description='''WeatherDesk - Change the wallpaper based on the weather
        (Uses the Yahoo! Weather API)''',
        formatter_class=argparse.RawTextHelpFormatter)

    arg_parser.add_argument(
        '-d', '--dir', metavar='directory', type=str,
        help='Specify wallpaper directory. Default: ~/.weatherdesk_walls\n\n',
        required=False)

    arg_parser.add_argument(
        '-f', '--format', metavar='format', type=str,
        help='Specify image file format. Default: .jpg\n\n',
        default='.jpg',
        required=False)

    arg_parser.add_argument(
        '-w', '--wait', metavar='seconds', type=int,
        help='Specify time (in seconds) to wait before updating. Default: 600\n\n',
        default=600,
        required=False)

    arg_parser.add_argument(
        '-n', '--naming', action='store_true',
        help='Show the image file-naming rules and exit.\n\n',
        required=False)

    arg_parser.add_argument(
        '--no-weather', action='store_true',
        help='Disable the weather functionality of the script. Wallpapers will only be changed based on the time of day.'
             'With this option, no internet connection is required.\n\n',
        required=False)

    arg_parser.add_argument(
        '-c', '--city', metavar='name', type=str,
        help=str('Specify city for weather. If not given, coordinates are taken from ipinfo.io.\n\n'),
        nargs='+', required=False)

    arg_parser.add_argument(
        '-o', '--one-time-run', action='store_true',
        help='Run once, then exit.\n\n',
        required=False)

    return vars(arg_parser.parse_args())


def validate_args(args):
    parsed_args = dict(args).copy()

    if not parsed_args['no_weather']:
        try:
            parsed_args['city'] = get_location(args['city'])
        except (urllib.error.URLError, ValueError):
            sys.stderr.write(
                'Finding ZIP from IP failed! Specify city manually with --city.')
            sys.exit(1)

    try:
        parsed_args['walls_dir'] = get_config_dir(args['dir'])
    except ValueError as e:
        sys.stderr.write(e)
        sys.exit(1)

    parsed_args['file_format'] = get_file_format(args['format'])

    parsed_args['wait_time'] = args['wait']  # ten minutes


    return parsed_args


def get_time_of_day(amanecer, atardecer):
 
    current_time = datetime.datetime.now()

    horas_sol = (atardecer - amanecer)/9
    bloque_sol = int((atardecer - amanecer)/9)
    bloque_luna = int((1440 - (atardecer - amanecer))/3)
    
    ahora = current_time.hour * 60 + current_time.minute
    
    if ahora in range(amanecer, amanecer+bloque_sol) :
      return '01'
    elif ahora in range(amanecer+bloque_sol, amanecer+bloque_sol*2) :
       return '02'
    elif ahora in range(amanecer+bloque_sol*2, amanecer+bloque_sol*3) :
       return '03'
    elif ahora in range(amanecer+bloque_sol*3, amanecer+bloque_sol*4) :
       return '04'
    elif ahora in range(amanecer+bloque_sol*4, amanecer+bloque_sol*5) :
       return '05'
    elif ahora in range(amanecer+bloque_sol*5, amanecer+bloque_sol*6) :
       return '06'
    elif ahora in range(amanecer+bloque_sol*6, amanecer+bloque_sol*7) :
       return '07'
    elif ahora in range(amanecer+bloque_sol*7, amanecer+bloque_sol*8) :
       return '08'
    elif ahora in range(amanecer+bloque_sol*8, amanecer+bloque_sol*9) :
       return '09'
    elif ahora in range(atardecer, atardecer+bloque_luna) :
       return '10'
    elif ahora in range(atardecer+bloque_luna, atardecer+bloque_luna*2) :
       return '11'
    else:
       return '12'
   


def get_weather_summary(weather_name):
    summaries = {'rain': ['drizzle', 'rain', 'shower'],
                 'wind': ['breez', 'gale', 'wind'],  # breez matches both breeze and breezy
                 'thunder': ['thunder'],
                 'snow': ['snow'],
                 'cloudy': ['cloud']}

    for summary, options in summaries.items():
        for option in options:
            if option in weather_name:
                return summary
    return 'normal'


def get_config_dir(config_dir_arg):
    if config_dir_arg:
        # User provided a directory
        walls_dir = os.path.abspath(config_dir_arg)

        if not os.path.isdir(walls_dir):
            raise ValueError('Invalid directory %s.' % walls_dir)
    else:
        walls_dir = os.path.join(os.path.expanduser('~'), '.weatherdesk_walls')

        if not os.path.isdir(walls_dir):
            os.mkdir(walls_dir)
            fmt = '''No directory specified.
    Creating in {}... Put files there or specify directory with --dir'''
            raise ValueError(fmt.format(walls_dir))
    return walls_dir


def get_file_format(file_format_arg):
    if not file_format_arg.startswith('.'):
        file_format_arg = '.' + file_format_arg

    return file_format_arg


def get_file_name(weather, daytime, walls_dir, file_format):
    if weather and daytime:
        name = '{}-{}'.format(daytime, weather)
    elif weather:
        name = weather
    elif daytime:
        name = daytime
    else:
        raise ValueError('Either a correct weather or a correct time is required.')

    return os.path.join(walls_dir, name + file_format)


def time_converter(time):
    converted_time = datetime.datetime.fromtimestamp(
        int(time)
    ).strftime('%I:%M %p')
    return converted_time


def get_location(city_arg):
    if not city_arg:
        location_json_url = 'http://ipinfo.io/json'
        location = json.loads(urlopen(location_json_url).read().decode('utf-8'))
        coords = location['loc']
        lat, lon = coords.split(',')
        return 'lat={}&lon={}'.format(lat, lon)
    elif isinstance(city_arg, list):
        city_arg = ''.join(city_arg)
        return 'q='+urllib.parse.quote(city_arg)

def get_current_weather(location, walls_dir, file_format):
    weather_json_url = 'https://api.openweathermap.org/data/2.5/weather?' + \
        location + '&appid=7bea90eeec1bc6de108b01600691aecd'

    weather_json = json.loads(urlopen(weather_json_url).read().decode('utf-8'))

    weather = str(weather_json['weather'][0]['main']).lower()

    amanece = time_converter(weather_json['sys']['sunrise'])
    
    amanece = amanece.split(':')
    hora_ama = amanece[0]
    min_ama = amanece[1].split()
    min_ama = min_ama[0]
    amanecer = int(hora_ama)*60 + int(min_ama)
    
    atardece = time_converter(weather_json['sys']['sunset'])
    
    atardece = atardece.split(':')
    hora_ata = atardece[0]
    min_ata = atardece[1].split()
    min_ata = min_ata[0]
    atardecer = (int(hora_ata)+12)*60 + int(min_ata)

    city_with_area = str(weather_json['name']) + ', ' + str(weather_json['sys']['country'])

    time_of_day = get_time_of_day(amanecer, atardecer)
    print('The current time of the day is {}'.format(time_of_day))

    weather_code = '' #get_weather_summary(weather)

    file_name = get_file_name(weather_code, time_of_day, walls_dir, file_format)
    print('Changing wallpaper to {}'.format(file_name))

    desktop_env = Desktop.get_desktop_environment()

    Desktop.set_wallpaper(file_name, desktop_env)

    return weather, city_with_area

def is_connected():
    try:
        host = socket.gethostbyname(REMOTE_SERVER)
        s = socket.create_connection((host, 80), 2)
        return True
    except:
        pass
        return False

def set_conditional_wallpaper(city, walls_dir, file_format):
    weather, actual_city = get_current_weather(city, walls_dir, file_format)
    print('The retrieved weather for {} is {}'.format(actual_city, weather))
   

def restart_program():
    # Restarts the current program, with file objects and descriptors cleanup

    new_weatherdesk_cmd = ''

    for i in sys.argv:
        new_weatherdesk_cmd = ' ' + i

    subprocess.Popen([new_weatherdesk_cmd], shell=True)

    sys.exit(0)


if __name__ == '__main__':

    args = get_args()
    parsed_args = validate_args(args)

    if parsed_args['naming']:
        print(NAMING_RULES.format(parsed_args['file_format']))
        sys.exit(0)

    if parsed_args['one_time_run']:
        set_conditional_wallpaper(parsed_args['city'],
                                  parsed_args['walls_dir'],
                                  parsed_args['file_format'])
        sys.exit(0)

    trace_main_loop = None

    while True:
        modified_args = parsed_args.copy();
        try:
            if not is_connected():
                print("No internet connection.")

            set_conditional_wallpaper(parsed_args['city'],
                                      parsed_args['walls_dir'],
                                      parsed_args['file_format'])

        except urllib.error.URLError:
            # Don't shut off on temporary network problems
            trace_main_loop = '[Main loop] \n' + traceback.format_exc()

            if sys.platform.startswith('linux'):
                # HACK: glibc on Linux only loads /etc/resolv.conf once
                # This breaks our network communications after suspend/resume
                # So we force it to reload using the res_init() function

                # But sometimes res_init() mysteriously crashes the program
                # and it's too low-level for any try-except to catch.

                # So we restart the whole thing!

                restart_program()

        except ValueError:
            # Sometimes JSON returns a null value for no reason

            trace_main_loop = '[Main loop] \n' + traceback.format_exc()

        except:
            # All other errors (except KeyboardInterrupt ^C)
            # We'll still have a full stack trace

            trace_main_loop = '[Main loop] \n' + traceback.format_exc()

        else:
            trace_main_loop = '[Main loop] No error.'

        finally:
            if trace_main_loop:
                print(trace_main_loop)

        time.sleep(parsed_args['wait_time'])
