import subprojects.types.Positions
import os


def print_header(is_close, session_id, output_path):
    aux = subprojects.types.Positions.PositionOutput()
    msg = aux.print_header()
    if is_close:
        filename = 'positions_'+session_id+'.txt'
    if not is_close:
        filename = 'curpositi_'+session_id+'.txt'

    f = open(output_path + '/' + filename, 'w')
    f.write(msg)
    f.close()


def print_data(is_close, session_id, output_path, positions_output):
    if is_close:
        filename = 'positions_'+session_id+'.txt'
    if not is_close:
        filename = 'curpositi_'+session_id+'.txt'

    try:
        os.stat(output_path+'/'+filename)
        if not is_close:
            aux = subprojects.types.Positions.PositionOutput()
            msg = aux.print_header()
            f = open(output_path + '/' + filename, 'w')
            f.write(msg)
            f.close()

    except:
        aux = subprojects.types.Positions.PositionOutput()
        msg = aux.print_header()
        f = open(output_path+'/'+filename, 'w')
        f.write(msg)
        f.close()

    if is_close:
        f = open(output_path+'/'+filename, 'a')
        for position in positions_output.close_data:
            msg = position.print_data()
            f.write(msg)
        f.close()

    if not is_close:
        f = open(output_path + '/' + filename, 'a')
        for position in positions_output.current_data:
            msg = position.print_data()
            f.write(msg)
        f.close()
