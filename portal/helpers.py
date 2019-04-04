from portal.models import *
import json, os, sys, csv

def reload_session_values(params):
	
	user = Signin_tbl.objects.get(
			username__iexact = params.session['username']
		)
		
	location_idx = user.location.all()	
	
	location_names = [l.name for l in location_idx]
	location_ids = [str(l.id) for l in location_idx]

	params.session['firstname'] = user.firstname.title()
	params.session['lastname'] = user.lastname.title()
	params.session['usertype'] = user.usertype
	params.session['email'] = user.email
	params.session['location_details'] = dict(zip(location_ids,location_names))
	params.session['location_ids'] = location_ids
	params.session['locations_assigned_count'] = len(location_ids)
	params.session['location_name'] = ', <br>'.join(location_names)



#===================================================================================
# Check file contents
#===================================================================================	
	
def check_data(file):	
	
	row_num = 1
	main_list = list()
	with open(os.path.dirname(__file__)+"/static/uploads/"+file, newline='') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',')
		
		for row in spamreader:
			ds = False
			if row_num > 1:
				category_id = row[7].strip()
				location_id = row[8].strip()
				
				if check_ipaddress(row[0].strip()):
					return (False,"Duplicate Entry/Null for Server in server_details column in the file at row : {}".format(row_num))
				
				if category_id!="" and location_id!="":
					if check_category_exists(category_id) and check_location_exists(location_id):
						ds = True
				else:
					return (False,"Category/Location ID is missing in the file at row : {}".format(row_num))
			
				if ds:
					main_list.append(row) 
				else:
					main_list = list()
					return (False,"Category/Location ID is invalid in the file at row : {}".format(row_num))	
				
			row_num += 1	
		
		return (True,main_list)	

#===================================================================================
# Check if the duplicate server_details
#===================================================================================
		
def check_ipaddress(ipaddress):
	if ipaddress.strip()!="":
		try:
			server = Server_tbl.objects.get(ipaddress__iexact = ipaddress)
			if server.ipaddress == ipaddress:
				return True
			return False	
		except Server_tbl.DoesNotExist:
			return False
	return True
		
		
#===================================================================================
# Check if the category exists
#===================================================================================	

def check_category_exists(category_id):
	if category_id.isnumeric():
		try:
			category = Category_tbl.objects.get(pk = category_id)			
			if category.id == int(category_id):
				return True
			return False	
		except Category_tbl.DoesNotExist:
			return False
	return False
		
			
#===================================================================================
# Check if the location exists
#===================================================================================	

def check_location_exists(location_id):
	if location_id.isnumeric():
		try:
			location = Location_tbl.objects.get(pk = location_id)
			if location.id == int(location_id):
				return True
			return False	
		except Location_tbl.DoesNotExist:
			return False
	return False		
			
			
#===================================================================================
# Write file contents to db
#===================================================================================			
			
def write_data_to_db(data):
	row_num = 0
	for row in data:
		
		try:
			server = Server_tbl(
				ipaddress = row[0].strip(),
				serial_number = row[1].strip(),
				model_number = row[2].strip(),
				warranty = row[3].strip(),
				admin_uid = row[4].strip(),
				admin_psw = row[5].strip(),
				status = row[6].strip(),
				category_id = row[7].strip(),
				location_id = row[8].strip(),
				os = row[9].strip(),
				ram = row[10].strip(),
				cpu = row[11].strip(),
				installed_softwares = row[12].strip(),
				server_name = row[13].strip(),
				global_ip = row[14].strip(),
				server_details = row[15].strip(),
			)
			
			server.save()
			row_num += 1
		except:
			return (False,"Duplicate Key")	

	return (True,"Rows Inserted : {}".format(row_num))	
	
	
#===================================================================================
# Location Selects
#===================================================================================	

def location_select(data):
	permissions = data
	servers = Server_tbl.objects.filter(location_id__in = permissions).values()
	return servers
	
		
