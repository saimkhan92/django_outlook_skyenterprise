import os
import re

def extract_configuration():

	email_directory=os.getcwd()+"/ztp/emails/"
	config_directory=os.getcwd()+"/ztp/configs/"
	email_list=os.listdir(email_directory)

	for file in email_list:
		print(email_directory+file)
		try:	#UnicodeDecodeError in presence of a hidden temp file
			with open(email_directory+file) as fh1:
				html_code=fh1.read()
				print(html_code)
				print(html_code)
				match1 = re.search('<pre>(.*[\s\S]*)</pre>', html_code)
				config=match1[1]
				print(config)
				match2=re.search('<p>Congratulations! You have successfully created device (.*).</p>', html_code)
				hostname=match2[1]
				print(hostname)
				with open(config_directory+hostname+".txt","w") as fh2:
					fh2.write("\n")
					fh2.write(config)
		except:
			continue
