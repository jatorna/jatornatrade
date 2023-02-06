import subprojects.types.Orders
import os


def print_header(session_id, output_path):
    aux = subprojects.types.Orders.OrderOutput()
    msg = aux.print_header()
    f = open(output_path+'/orders_'+session_id+'.txt', 'w')
    f.write(msg)
    f.close()


def print_data(session_id, output_path, orders_output):
    try:
        os.stat(output_path+'/orders_'+session_id+'.txt')
    except:
        aux = subprojects.types.Orders.OrderOutput()
        msg = aux.print_header()
        f = open(output_path + '/orders_' + session_id + '.txt', 'w')
        f.write(msg)
        f.close()

    f = open(output_path + '/orders_' + session_id + '.txt', 'a')
    for order in orders_output.data:
        msg = order.print_data()
        f.write(msg)
    f.close()
