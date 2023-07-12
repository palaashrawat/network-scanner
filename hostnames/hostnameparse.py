import pandas as pd
import os 

# Read the Excel file
filepath = os.path.join('hostnames', 'IP and Hostnames.xlsx')
print(filepath)
df = pd.read_excel(filepath)

# Filter the rows by Type and extract the relevant values from the Data column
name_servers = df.loc[df['Type'] == 'Name Server (NS)', 'Data'].str.split('.').str[0]
hosts = df.loc[df['Type'] == 'Host (A)', 'Data']

# Convert the extracted values to lists
name_servers_list = name_servers.tolist()
hosts_list = hosts.tolist()

newfile = open('NameServerList.txt', "w+")
newfile.write(str(name_servers_list))
newfile.close()

newfile = open('HostsList.txt', "w+")
newfile.write(str(hosts_list))
newfile.close()
