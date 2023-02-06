import subprojects.misc.LowLevelFuncions as llf
import datetime as dt

logger = llf.script_logger('SCREENER PARSER')


def parse_screener_file(file_path):

    screener_data = {}
    try:
        with open(file_path) as f:
            lines = f.readlines()

    except Exception as e:
        logger.error(e)
        return False

    i = 0
    for line in lines:
        if i == 0:
            i += 1
            continue

        line_splt = line.split(' ')
        epoch = dt.datetime.strptime(line_splt[0].rstrip('\n'), '%m/%d/%Y')
        symbol_list = set()
        for symbol in line_splt[1:]:
            if symbol.rstrip('\n') != '':
                symbol_list.add(symbol.rstrip('\n'))

        screener_data[epoch] = symbol_list
        i += 1

    return screener_data

