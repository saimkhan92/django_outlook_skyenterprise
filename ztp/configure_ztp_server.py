
import csv
import sys
from jinja2 import Template
from subprocess import call
import os
from shutil import copyfile

# Note: Junos image files and configuration files reside in the default apache2 directory /var/www/html
csv_file_path=os.getcwd()+"/ztp/host_to_mac_mapping.csv"
apache_directory_path="/var/www/html/"
dhcpd_file_path="/etc/dhcp/dhcpd.conf"
dhcpd_restart_command="sudo /etc/init.d/isc-dhcp-server restart"
configs_directory_path=os.getcwd()+"/ztp/configs"

csv_list_of_dicts = csv.DictReader(open(csv_file_path))

# read from csv, take parameters, render via jinja2base_set_tempate and generate a specific base config per device, store it in temp folder, name it using hostname
# read from skyenterprise config directory and append to appropriate base config device file based on hostname
# push config file to apache http folder
# fillout hostname, mac in base dhcp template and append to actual file, for this step refer previous ztp program
# Code in 1 hour test in 2 hours

with open(os.getcwd()+"/ztp/templates/junos_base_set_config.j2","r") as fh1:
    set_template_text=fh1.read()
set_template=Template(set_template_text)

for row in csv_list_of_dicts:
    with open(os.getcwd()+"/ztp/temp/"+row["skyent_hostname"]+".txt","w") as fh2:
        fh2.write(set_template.render(row))
        if row["skyent_hostname"]+".txt" in os.listdir(configs_directory_path):
            print("SkyEnterprise outbound SSH configuration of the device "+row["skyent_hostname"]+" found in "+configs_directory_path)
            with open(configs_directory_path+"/"+row["skyent_hostname"]+".txt","r") as fh3:
                ssh_config=fh3.read()
                fh2.write(ssh_config)
        else:
            print("SkyEnterprise outbound SSH configuration of the device does not exist in "+configs_directory_path+". SSH configuration not generated")
            continue

def main():
    print("")

if __name__=="__main__":
    main()
