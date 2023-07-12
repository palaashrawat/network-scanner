import mailer
import portscanner
import pandas as pd
from pretty_html_table import pretty_html_table, build_table
import ast

def make_table(diff): 
    table_data = []
    for network, ip_dict in diff.items():
        for ip, open_ports in ip_dict.items():
            table_data.append([network, ip, ", ".join(map(str, open_ports))])
    
    table_headers = ["Network Structure", "IP/Hostname", "Open Ports"]

    df = pd.DataFrame(table_data, columns=table_headers)

    return df

def read_hostnames(): 
    # Read 'NameServerList.txt' into an array
    with open('hostnames/NameServerList.txt', 'r') as file:
        name_servers_content = file.read()
        name_servers_array = ast.literal_eval(name_servers_content)

    # Read 'HostsList.txt' into an array
    with open('hostnames/HostsList.txt', 'r') as file:
        hosts_content = file.read()
        hosts_array = ast.literal_eval(hosts_content)

    # Print the arrays
    return name_servers_array, hosts_array

def main(): 
    ns_array, host_array = read_hostnames()

    host_range = host_array + ns_array

    ps = portscanner.PortScannerClass(host_range)
    open, continued, closed, yfname, tfname,  = ps.main()

    df_open = make_table(open)
    df_continued = make_table(continued)
    df_closed = make_table(closed)

    html_open_table = build_table(df_open, 'blue_light', font_family='Calibri', font_size='small')
    html_continued_table = build_table(df_continued, 'blue_light', font_family='Calibri', font_size='small')
    html_closed_table = build_table(df_closed, 'blue_light', font_family='Calibri', font_size='small')

    m = mailer.MailerClass(html_open_table, html_continued_table, html_closed_table, yfname, tfname)
    m.main()


if __name__ == '__main__': 
    main()