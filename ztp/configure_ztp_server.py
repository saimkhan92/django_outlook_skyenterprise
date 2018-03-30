
import csv
import sys
from jinja2 import Template
from subprocess import call
import os
from shutil import copyfile

def generate_final_config():
    # Note: Junos image files and configuration files reside in the default apache2 directory /var/www/html
    csv_file_path=os.getcwd()+"/ztp/host_to_mac_mapping.csv"
    dhcpd_file_path="/etc/dhcp/dhcpd.conf"
    dhcpd_restart_command="sudo /etc/init.d/isc-dhcp-server restart"
    configs_directory_path=os.getcwd()+"/ztp/configs"
    csv_list_of_dicts = csv.DictReader(open(csv_file_path))

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

def generate_final_dhcpd_config():
    csv_file_path=os.getcwd()+"/ztp/host_to_mac_mapping.csv"
    csv_list_of_dicts = csv.DictReader(open(csv_file_path))
    apache_directory_path="/var/www/html/"
    dhcpd_template_path=os.getcwd()+"/ztp/templates/saim_isc-dhcpd_template.j2"
    base_dhcp_conf_path=os.getcwd()+"/ztp/templates/base_dhcp_config.txt"
    final_dhcpd_conf_path=os.getcwd()+"/ztp/temp/dhcpd.conf"

    with open(os.getcwd()+"/ztp/templates/isc-dhcpd_template.j2","r") as fh1:
        dhcpd_template_text=fh1.read()
    dhcpd_template=Template(dhcpd_template_text)

    with open(base_dhcp_conf_path,"r") as fh2:
        dhcp_base_text=fh2.read()
        with open(final_dhcpd_conf_path,"w") as fh3:
            fh3.write(dhcp_base_text)

    for row in csv_list_of_dicts:
        with open(final_dhcpd_conf_path,"a") as fh4:
            dhcp_device_entry=dhcpd_template.render(row)
            fh4.write(dhcp_device_entry)

def copy_files():
    final_dhcpd_conf_path=os.getcwd()+"/ztp/temp/dhcpd.conf"
    dhcpd_restart_command="sudo /etc/init.d/isc-dhcp-server restart"

    os.chmod(final_dhcpd_conf_path,0o777)
    copyfile(final_dhcpd_conf_path,"/etc/dhcp/dhcpd.conf")
    dhcpd_return_code = call(dhcpd_restart_command, shell=True)

# cp all contents of temp folder to apache http folder (one copy command)
# render dhcpd.conf file pieces using base_template+csv file, add all the pieces togther
# append the added pieces to base dhcpd.conf (containing all juniper options)
# transfer the created file to /etc/dhcp/dhcpd.conf

def main():
    print("")
    generate_final_config()
    generate_final_dhcpd_config()

if __name__=="__main__":
    main()
