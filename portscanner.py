import mailer
import nmap
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import ipaddress
import re
import socket
import os
import concurrent.futures
import logging


class PortScannerClass():
    ''' Creates and performs necessary Port Scanning Tasks '''

    def __init__(self, host_range):
        self.hosts = host_range
    
    def get_ip_type(self): 
        ip_type_dict = {}

        for ip in self.hosts: 
            if re.match(r'^[a-zA-Z0-9-]+$', ip):
                ip_type_dict[ip] = 'hostname'
            else:
                try:
                    ip_obj = ipaddress.ip_address(ip)
                    ip_type_dict[ip] = 'address'
                except ValueError:
                    try:
                        ip_obj = ipaddress.ip_network(ip)
                        ip_type_dict[ip] = 'network'
                    except ValueError:
                        pass
        return ip_type_dict
    
    def perform_network_scan(self, ip_type_dict): 
        scanner = nmap.PortScanner()
    
        # create ip_type_dict
        active_host_list = {}
        for host, type in ip_type_dict.items(): 
            try: 
                if type == 'network': 
                    active_ips = []
                    network_scan = scanner.scan(hosts = host, arguments='-sn --max-rate 10000')
                    result = network_scan['scan']
                    for ip, details in result.items(): 
                        if details['status']['state'] == 'up': 
                            active_ips.append(ip)
                    active_host_list[host] = active_ips
                elif type == 'address': 
                    active_host_list[host] = [host]
                elif type == 'hostname': 
                    ip_address = socket.gethostbyname(host)
                    active_host_list[host] = ip_address
                else: 
                    continue
            except Exception as e: 
                logging.info(f'Perform Network Scan Exception: {e}')
                logging.info(f'Here is the problem host: {host}')
                continue
                
        return active_host_list

    def scan_ip(self, ip): 
        scanner = nmap.PortScanner()

        open_ports = []
        ip_scan = scanner.scan(hosts=ip, arguments = '-F --max-rate 1000') #0 -T5')
        scan_result = ip_scan['scan']

        for ip, port in scan_result.items():
            try:
                for open_port, details in port['tcp'].items():
                    if details['state'] == 'open':
                        open_ports.append(open_port)
            except:
                pass
        
        return ip, open_ports
    
    def get_open_ports(self, active_ip_dict):
        result = {}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_network = {executor.submit(self.scan_ip, ip): network for network, ip_list in active_ip_dict.items() for ip in ip_list}

            for future in concurrent.futures.as_completed(future_to_network):
                ip, open_ports = future.result()
                network = future_to_network[future]

                if network not in result: 
                    result[network] = {}
                
                result[network][ip] = open_ports
            
            return result 
        
    def create_today_file(self, today_dict):
        now = datetime.now()
        today_date = now.strftime("%d-%m-%Y")
        today_filename = "textfiles/" + today_date + ".txt"
        
        today_json = json.dumps(today_dict)
        newfile = open(today_filename, "w+")
        newfile.write(today_json)
        newfile.close()

        return today_filename


    def get_recent_file(self):
        now = datetime.now()
        yesterday = now - timedelta(1)
        yesterday_date = yesterday.strftime("%d-%m-%Y")
        yesterday_filename = "textfiles/" + yesterday_date + ".txt"

        if os.path.isfile(yesterday_filename):
            with open(yesterday_filename, "r+") as yesterday_scan:
                yesterday_ip_dict = json.loads(yesterday_scan.read())
            return yesterday_filename, yesterday_ip_dict
        else: 
            files_in_dir = os.listdir("textfiles")
            files = [file for file in files_in_dir if os.path.isfile(os.path.join("textfiles", file))]

            def get_file_date(filename):
                file_date, file_ext = os.path.splitext(filename)
                if file_ext.lower() == '.txt':
                    try:
                        return datetime.strptime(file_date, "%d-%m-%Y")
                    except ValueError:
                        return None
                return None

            files = [file for file in files if get_file_date(filename=file) is not None]
            files.sort(key=get_file_date, reverse=True)

            for file in files: 
                file_date = get_file_date(file)
                if file_date.date() < now.date():  # Compare only date part (day, month, year)
                    yesterday_filename = os.path.join("textfiles", file)
                    with open(yesterday_filename, "r+") as yesterday_scan:
                        yesterday_ip_dict = json.loads(yesterday_scan.read())
                    return yesterday_filename, yesterday_ip_dict


    # define functions to compare results from yesterday and today's scans - getting the diff 
    def compare_ports(self, yesterday, today):
        new_network = {}
        continued_network = {}
        closed_network = {}

        for network, ip_dict_today in today.items():
            ip_dict_yesterday = yesterday.get(network, {})

            for ip, ports_today in ip_dict_today.items():
                ports_yesterday = ip_dict_yesterday.get(ip, [])

                new_ports = [port for port in ports_today if port not in ports_yesterday]
                common_ports = [port for port in ports_today if port in ports_yesterday]
                closed_ports = [port for port in ports_yesterday if port not in ports_today]

                if new_ports:
                    new_network.setdefault(network, {})[ip] = new_ports
                if common_ports:
                    continued_network.setdefault(network, {})[ip] = common_ports
                if closed_ports:
                    closed_network.setdefault(network, {})[ip] = closed_ports

        return new_network, continued_network, closed_network
    
    def main(self):
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
        logging.info('Steps to complete: \nGet IP Type \nPerform Network Scan \nGet Open Ports \nCreate Today File \nGet Recent File \nComparison')

        hosts_range_dict = self.get_ip_type()
        logging.info('Get IP Type - Completed')

        active_host_dict = self.perform_network_scan(hosts_range_dict)
        logging.info('Perform Network Scan - Completed')

        today_ip_dict = self.get_open_ports(active_host_dict)
        logging.info('Get Open Ports - Completed')

        today_filename = self.create_today_file(today_ip_dict)
        logging.info('Create Today File - Completed')

        yesterday_filename, yesterday_ip_dict = self.get_recent_file()
        logging.info('Get Recent File - Completed')

        open, continued, closed = self.compare_ports(yesterday_ip_dict, today_ip_dict)
        logging.info('Comparison - Completed')

        return open, continued, closed, yesterday_filename, today_filename


def main():
    PortScannerClass.main()

if __name__ == '__main__': 
    main()