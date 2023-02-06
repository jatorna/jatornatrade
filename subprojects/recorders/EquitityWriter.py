import subprojects.types.Equity
import os


def print_header(session_id, output_path):
    aux = subprojects.types.Equity.EquityOutput()
    msg = aux.print_header()
    f = open(output_path+'/equity_'+session_id+'.txt', 'w')
    f.write(msg)
    f.close()


def print_data(session_id, output_path, equity_output):
    try:
        os.stat(output_path+'/equity_'+session_id+'.txt')
    except:
        aux = subprojects.types.Equity.EquityOutput()
        msg = aux.print_header()
        f = open(output_path + '/equity_' + session_id + '.txt', 'w')
        f.write(msg)
        f.close()

    msg = equity_output.print_data()
    f = open(output_path+'/equity_'+session_id+'.txt', 'a')
    f.write(msg)
    f.close()
