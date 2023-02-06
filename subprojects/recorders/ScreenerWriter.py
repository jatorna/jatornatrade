import subprojects.types.ScreenerData
import os


def print_header(session_id, output_path):
    aux = subprojects.types.ScreenerData.ScreenerOutputData()
    msg = aux.print_header()
    f = open(output_path+'/screener_data_' + session_id + '.txt', 'w')
    f.write(msg)
    f.close()


def print_data(session_id, output_path, screener_output):
    try:
        os.stat(output_path+'/screener_data_'+session_id+'.txt')
    except:
        aux = subprojects.types.ScreenerData.ScreenerOutputData()
        msg = aux.print_header()
        f = open(output_path + '/screener_data_' + session_id + '.txt', 'w')
        f.write(msg)
        f.close()

    f = open(output_path + '/screener_data_' + session_id + '.txt', 'a')
    msg = screener_output.print_data()
    f.write(msg)
    f.close()
