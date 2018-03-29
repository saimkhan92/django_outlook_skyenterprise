import os
from bs4 import BeautifulSoup

email_directory=os.getcwd()+"/ztp/emails/"
config_directory=os.getcwd()+"/ztp/configs/"
email_list=os.listdir(email_directory)

for file in email_list:
	with open(email_directory+file) as fh1:
		html_code=fh1.read()
		#print(html_code+"\n\n\n")
		soup = BeautifulSoup(html_code)
		confg=soup.pre.string
		print(soup.p.string)

"""
email_directory=os.getcwd()+"/ztp/emails/"
config_directory=os.getcwd()+"/ztp/configs/"
email_list=os.listdir(email_directory)

for file in email_list:
	with open(email_directory+file) as fh1:
		text=fh1.read()
		splitted_text=text.split("\n")
		print(splitted_text)

		for line in splitted_text:
			if line.split():
				if line.split()[0]=="Congratulations!":
					hostname=line.split()[len(line.split())-1][:-1]
					print("hostname: "+hostname)

		with open(config_directory+hostname+".txt","w") as fh2:
			for line in splitted_text:
				if line.split():
					if line.split()[0]=="set":
						fh2.write(line)
						fh2.write("\n")
"""
