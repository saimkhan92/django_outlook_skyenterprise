import csv
import sys
import paramiko
from jinja2 import Template
from subprocess import call
import os
from shutil import copyfile
import re

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
        print(dhcpd_template_text)
    dhcpd_template=Template(dhcpd_template_text)

    with open(base_dhcp_conf_path,"r") as fh2:
        dhcp_base_text=fh2.read()
        with open(final_dhcpd_conf_path,"w") as fh3:
            fh3.write(dhcp_base_text)

    for row in csv_list_of_dicts:
        print (row)
        with open(final_dhcpd_conf_path,"a") as fh4:
            dhcp_device_entry=dhcpd_template.render(row)
            print(dhcp_device_entry)
            fh4.write(dhcp_device_entry)

def copy_files():
    final_dhcpd_conf_path=os.getcwd()+"/ztp/temp/dhcpd.conf"
    dhcpd_restart_command="sudo /etc/init.d/isc-dhcp-server restart"

    os.chmod(final_dhcpd_conf_path,0o777)
    copyfile(final_dhcpd_conf_path,"/etc/dhcp/dhcpd.conf")
    dhcpd_return_code = call(dhcpd_restart_command, shell=True)

def scp_files():
    hostname="10.2.128.4"    #local ZTP VM
    username="saimkhan"
    password="310892"
    port=22
    t = paramiko.Transport((hostname, 22))
    t.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(t)

    for filename in os.listdir("./ztp/temp"):
        mypath="./ztp/temp/"+filename
        if  filename=="dhcpd.conf":
            print("dhcpd file transfer")
            #os.chmod(mypath,0o777)
            remotepath="/etc/dhcp/dhcpd.conf"
            sftp.put(mypath, remotepath)
        elif filename[-4:]=="conf":
            print("conf transfer")
            #os.chmod(mypath,0o777)
            remotepath="/var/www/html/"+filename
            sftp.put(mypath, remotepath)

    #### Added to include a workaround testing
    for filename in os.listdir("./ztp/temp"):
        mypath="./ztp/temp/"+filename
        if  filename=="dhcpd.conf":
            continue
        elif filename[-3:]=="txt":
            print("txt transfer")
            #os.chmod(mypath,0o777)
            remotepath="/var/tmp/"+filename
            sftp.put(mypath, remotepath)
    sftp.put("./ztp/host_to_mac_mapping.csv", "/var/tmp/host_to_mac_mapping.csv")
    t.close()

def set_to_text_config():
    csv_file_path=os.getcwd()+"/ztp/host_to_mac_mapping.csv"
    csv_list_of_dicts = csv.DictReader(open(csv_file_path))
    set_config_dir="./ztp/configs"
    variable_dict={}

    with open(os.getcwd()+"/ztp/templates/junos_base_text_config.j2","r") as fh1:
        text_template_content=fh1.read()
    text_template=Template(text_template_content)

    for row in csv_list_of_dicts:
        with open("./ztp/temp/"+row["skyent_hostname"]+".txt","r") as fh:
            set_file_text=fh.read()
            variable_dict["hostname"] = (re.search('set system host-name (.*)', set_file_text))[1]
            variable_dict["nameserver"] = (re.search('set system name-server (.*)', set_file_text))[1]
            variable_dict["encrypted_pwd"] = (re.search('set system root-authentication encrypted-password "(.*)"', set_file_text))[1]
            variable_dict["skyent_pwd"] = (re.search('set system login user skyenterprise authentication encrypted-password (.*)', set_file_text))[1]
            variable_dict["ncd01_device_id"] = (re.search('set system services outbound-ssh client skyenterprise-ncd01 device-id (.*)', set_file_text))[1]
            variable_dict["ncd01_secret"] = (re.search('set system services outbound-ssh client skyenterprise-ncd01 secret (.*)', set_file_text))[1]
            variable_dict["ncd02_device_id"] = (re.search('set system services outbound-ssh client skyenterprise-ncd02 device-id (.*)', set_file_text))[1]
            variable_dict["ncd02_secret"] = (re.search('set system services outbound-ssh client skyenterprise-ncd02 secret (.*)', set_file_text))[1]
            print(variable_dict)
            #print(os.getcwd()+"/ztp/temp/"+file[-4:]+".conf")
            with open(os.getcwd()+"/ztp/temp/"+row["skyent_hostname"]+".conf","w") as fh2:
                #print(text_template.render(variable_dict))
                fh2.write(text_template.render(variable_dict))

def clear_directory():
    deletion_dir_list=["./ztp/configs","./ztp/emails","./ztp/temp"]
    for dir in deletion_dir_list:
        files=os.listdir(dir)
        for file in files:
            os.remove(dir+"/"+file)

def main():
    print("")
    #generate_final_config()
    #generate_final_dhcpd_config()
    #copy_files()
    #scp_files()

if __name__=="__main__":
    main()
