import logging
import datetime as dt
import os
import numpy as np
import urllib.request


###########################################################
#  LOGGER FUNCTIONS      ##################################
###########################################################

def script_logger(module_name):
    logger = logging.getLogger(module_name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(levelname)-8s] [%(name)-17s] %(message)s', '%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logging.addLevelName(5, 'OK')
    logger.setLevel(5)
    return logger


logger = script_logger('LOW LEVEL FUNC')


###########################################################
#  SYSTEM FUNCTIONS      ##################################
###########################################################

def create_folder_if_not_exists(path):
    # OLD, sustituible por un os.makedir con parametro de que no existe
    if not os.path.exists(path):
        os.makedirs(path)


###########################################################
#  PROGRAM FUNCTIONS      #################################
###########################################################

def get_input_value(tag, str_list, default_value, **kwargs):
    # TODO: list managing: to be able of acquire a list of *type* from a string input -> standarized list conversion
    short_tag = kwargs.get('short_tag', None)
    options_list = kwargs.get('options', [])
    value_type = kwargs.get('type', str)
    value = default_value

    if len(str_list) > 1:
        for index in range(0, len(str_list) - 1):
            if str_list[index] == tag:
                value = str_list[index + 1]
                logger.debug('Input value of \"%s\" found for tag \"%s\"' % (value, tag))
                break
            elif str_list[index] == short_tag:
                value = str_list[index + 1]
                logger.debug('Input value of \"%s\" found for short tag \"%s\"' % (value, tag))
                break
            if index == len(str_list) - 2:
                logger.debug('Input tag \"%s\" not found in input list. Default value: \"%s\"' % (tag, value))
                return default_value

    try:
        value = value_type(value)
    except ValueError:
        logger.warning('Problems converting input value of \"%s\" (for tag \"%s\") to %s type. '
                       'Default value (\"%s\") assigned.' % (value, tag, value_type, default_value))
        return default_value

    if len(options_list) > 0 and type(options_list) == list and value not in options_list:
        logger.error('Input value \"%s\" for tag \"%s\" not found in options list ( %s ). Assigned value: \"%s\"'
                     % (value, tag, options_list, default_value))
        return default_value
    else:
        return value


def check_input_tag(tag, str_list, tag_present_value, tag_not_present_value, **kwargs):
    short_tag = kwargs.get('short_tag', None)
    value = tag_not_present_value
    if tag in str_list:
        logger.debug('Tag \"%s\" found in input list' % tag)
        value = tag_present_value
    elif short_tag in str_list:
        logger.debug('Tag \"%s\" found in input list' % short_tag)
        value = tag_present_value
    else:
        logger.debug('Tag \"%s\" not found in input list' % tag)
    return value


def check_options(value, options_list, negative_return=False, positive_return='value'):
    if positive_return == 'value':
        positive_return = value
    if value not in options_list:
        return negative_return
    else:
        return positive_return


def update_attribute(target_object, attribute_tag, inputs_dict, default_value=None, input_dict_key='',
                     force_default_definition=False, **kwargs):
    value_type = kwargs.get('type', None)
    options_list = kwargs.get('options_list', None)

    if input_dict_key == '':
        input_dict_key = attribute_tag

    if attribute_tag is None or not type(attribute_tag) == str or not len(attribute_tag) > 0:
        logger.error('update_attribute::A not valid attribute tag has been received as input ()')
        return

    bool_apply_value = False
    if input_dict_key not in inputs_dict or (
            options_list is not None and inputs_dict[input_dict_key] not in options_list):
        value = default_value
        if force_default_definition:
            bool_apply_value = True
    else:
        value = inputs_dict[input_dict_key]
        bool_apply_value = True

    if bool_apply_value:
        if value_type is None or type(default_value) == value_type:
            setattr(target_object, attribute_tag, value)
        else:
            setattr(target_object, attribute_tag, value_type(value))


def get_dict_value(tag, dictionary, default_value, **kwargs):
    short_tag = kwargs.get('short_tag', None)
    options_list = kwargs.get('options', [])
    value_type = kwargs.get('type', None)
    value = default_value

    if not type(dictionary) == dict or len(dictionary) == 1:
        return value

    for key in dictionary:
        if key == tag or key == short_tag:
            value = dictionary[key]
            break

    if value_type is not None:
        try:
            value = value_type(value)
        except ValueError:
            return default_value

    if type(options_list) == list and len(options_list) > 0 and value not in options_list:
        return default_value

    return value


###########################################################
#  DATE      ##############################################
###########################################################

def datetime_exists_in_tz(dt, tz):
    try:
        dt.tz_localize(tz)
        return True
    except:
        return False

def round_date(date):
    t = date
    s = t.strftime('%Y %m %d %H %M %S.%f')
    tail = s[-7:]
    f = round(float(tail), 3)
    temp = "%.3f" % f
    epoch_str = "%s%s" % (s[:-7], temp[1:])
    epoch = dt.datetime.strptime(epoch_str, '%Y %m %d %H %M %S.%f')
    if float(tail) >= 0.9995:
        deltatime = dt.timedelta(seconds=1)
        epoch = epoch + deltatime
    return epoch


def round_time(date_time, roundto=60):
    seconds = (date_time.replace(tzinfo=None) - date_time.min).seconds
    rounding = (seconds + roundto / 2) // roundto * roundto
    return date_time + dt.timedelta(0, rounding - seconds, -date_time.microsecond)


def datetime64_to_datetime(dt64):
    ts = (dt64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
    date = dt.datetime.utcfromtimestamp(ts)
    return date


def next_monday_9am():
    d = dt.datetime.now()
    days_ahead = 0 - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7

    return dt.datetime((d + dt.timedelta(days_ahead)).year, (d + dt.timedelta(days_ahead)).month,
                       (d + dt.timedelta(days_ahead)).day, 9, 0, 0)


def next_monday():
    d = dt.datetime.now()
    days_ahead = 0 - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7

    return dt.datetime((d + dt.timedelta(days_ahead)).year, (d + dt.timedelta(days_ahead)).month,
                       (d + dt.timedelta(days_ahead)).day, 0, 0, 0)


def internet_connection(host='http://google.com'):
    try:
        urllib.request.urlopen(host)
        return True
    except:
        return False
