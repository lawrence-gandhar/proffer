"""
*	Author	: Lawrence Gandhar
*	Project	: Server Password Managment System	
*	AppName	: PROFFER
*	Date	: 24-May-2018
*	Version	: 1.0.0
* 	Database: PostgreSQL
"""

from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.db import IntegrityError
from portal.models import *
import sys, os, csv, json, xlwt
from portal.helpers import *
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.core.paginator import Paginator

# Create your views here.


#===================================================================================
# Whitelist Ips
#===================================================================================

def restrict_access(ipaddress):
	ip_list = [	
				'172.23.7.165', 
				'172.23.7.158', 
				'172.23.5.105',
				'172.23.7.7',
				'10.1.0.144', 
				'10.1.1.52', 
				'192.168.118.46',
				'192.168.116.100',  
				'172.23.7.119',
				'10.57.4.133',  
				'192.168.118.248',
				'172.23.7.44',
				'10.64.45.67', 
				'172.23.5.28', 
				'172.23.7.155',
				'172.23.7.201', 
				'10.57.3.171',  
				'10.64.45.33', 
				'10.64.45.246',                      
			]
	
	if ipaddress in ip_list:
		return True	
	return False

#===================================================================================
# Index Page
#===================================================================================

def index(request):
	if restrict_access(request.META['REMOTE_ADDR']):

		if request.POST:
			if request.POST["username"] and request.POST["password"]:
				try:
					user = Signin_tbl.objects.get(
							username__iexact = request.POST["username"],
							password__iexact = request.POST["password"], 
							status = Signin_tbl.ACTIVE
						)
						
					location_idx = user.location.all()	
					
					location_names = [l.name for l in location_idx]
					location_ids = [str(l.id) for l in location_idx]
						
					request.session['logged_in'] = True
					request.session['key'] = request.session.session_key
					request.session['username'] = user.username
					request.session['usertype'] = user.usertype
					request.session['firstname'] = user.firstname.title()
					request.session['lastname'] = user.lastname.title()
					request.session['id'] = user.id
					request.session['email'] = user.email
					request.session['location_details'] = dict(zip(location_ids,location_names))
					request.session['location_ids'] = location_ids
					request.session['locations_assigned_count'] = len(location_ids)
					request.session['location_name'] = ', <br>'.join(location_names)
										
					if not request.session.session_key:
						request.session.save()
						
					return redirect('dashboard/')
					
				except Signin_tbl.DoesNotExist:
					return render(request,"portal/index.html",{'error':'Login Failed'})
				
		return render(request,"portal/index.html",{})	
	return HttpResponse(status = 503)

#===================================================================================
# Logout Method
#===================================================================================	

def logout(request):
	if restrict_access(request.META['REMOTE_ADDR']):
		if 'logged_in' in request.session:
			if request.session['logged_in'] == True:
				from django.contrib.auth import logout	
				request.session['logged_in'] = False
				return render(request,"portal/logout.html")	
			return HttpResponse(status=404)			
		return HttpResponse(status=404)	
	return HttpResponse(status=503)	
	

#===================================================================================
# Dashboard Method
#===================================================================================	

def dashboard(request):
	if restrict_access(request.META['REMOTE_ADDR']):
		if 'logged_in' in request.session:
			if request.session['logged_in'] == True:

				reload_session_values(request)
				
				user = Signin_tbl.objects.get(pk = request.session["id"])
				
				permissions = Permissions.objects.get(user = user.id)
				
				server_ids = permissions.server.all()
				server_ids = [str(s.id) for s in server_ids]
				
				perm = 0
				filter = "ALL ASSETS IN ASSIGNED LOCATIONS"
				total_records = 0
				query_string = ""
				records_per_page = 30
				
				f = request.GET.get('f', False)
				a = request.GET.get('a', False)
				page = request.GET.get('page')
				
				if 'a' in request.GET:
					a = request.GET['a']
					
					filter = "Access Denied"
					server_list_main = Server_tbl.objects.filter(
								status = Server_tbl.ACTIVE,
								location_id__in = request.session['location_ids']
							).exclude(id__in = server_ids)
							
					if a == '1':
						filter = "Access Granted"
					
						server_list_main = Server_tbl.objects.filter(
								status = Server_tbl.ACTIVE,
								id__in = server_ids
							)
						
					server_list = server_list_main.values()	
					total_records = server_list_main.count()
					
				elif 'f' in request.GET:
					f = request.GET['f']
					
					filter = request.session['location_details'][f]
					
					server_list_main = Server_tbl.objects.filter(
							status = Server_tbl.ACTIVE,
							location_id = int(f)
						)
						
					server_list = server_list_main.values()	
					total_records = server_list_main.count()	
									
				else:
					server_list_main = Server_tbl.objects.filter(
							status = Server_tbl.ACTIVE,
							location__in = request.session['location_ids']
						)
					server_list = server_list_main.values()	
					total_records = server_list_main.count()	
				
				server_list_page = Paginator(server_list, records_per_page)
				server_list = server_list_page.get_page(page)
				
				if server_list.has_next() or server_list.has_previous():
					if 'a' in request.GET:
						query_string = "a="+str(a)+"&"
					elif 'f' in request.GET:
						query_string = "f="+str(f)+"&"
					else:
						query_string = ""
						
					
				data = dict({
					'query_string':query_string,
					'records_per_page':records_per_page,
					'server_list':server_list,
					'access_servers':len(server_ids),
					'permitted_servers':server_ids,
					'locations_assigned_count':request.session["locations_assigned_count"],
					'location_count':Server_tbl.objects.filter(location_id__in = request.session['location_ids'], status = Server_tbl.ACTIVE).count(),
					'total_count':Server_tbl.objects.filter(status = Server_tbl.ACTIVE).count(),
					'name' : request.session["firstname"].title()+" "+request.session["lastname"].title(),
					'email' : request.session["email"],
					'location_list':request.session["location_details"],
					'filter':filter,
					'total_records':total_records,
					'usertype':request.session["usertype"],
				})
				
				return render(request,'portal/dashboard.html',data)
			return HttpResponse(status=404)	
		return HttpResponse(status=404)		
	return HttpResponse(status=503)		
	
#===================================================================================
# Get Password Method
#===================================================================================				
	
def get_password(request):
	if restrict_access(request.META['REMOTE_ADDR']):
		if 'logged_in' in request.session:
			if request.session['logged_in'] == True:
				try:
					server = Server_tbl.objects.get(pk = request.POST["ref_id"])
					return HttpResponse(server.admin_psw)	
				except Server_tbl.DoesNotExist:
					return HttpResponse(status=500)	
			return HttpResponse(status=404)	
		return HttpResponse(status=404)	
	return HttpResponse(status=503)	

#===================================================================================
# Import CSV Method
#===================================================================================		

def import_csv(request):
	if restrict_access(request.META['REMOTE_ADDR']):
		if 'logged_in' in request.session:
			if request.session['logged_in'] == True:
			
				reload_session_values(request)
				
				data = dict({
					'category_list': Category_tbl.objects.filter(status = Category_tbl.ACTIVE).values(),
					'location_list': Location_tbl.objects.filter(status = Location_tbl.ACTIVE).values(),
					'name' : request.session["firstname"].title()+" "+request.session["lastname"].title(),
					'email' : request.session["email"],
					'msg' : "",
					'error' : 0,
				})
							
				if request.POST:
					
					myfile = request.FILES['file']
					file = myfile.name
					
					if file.endswith('.csv') or file.endswith('.CSV'):
						
						if os.path.isfile(os.path.dirname(__file__)+"/static/uploads/"+file):
								
							with open(os.path.dirname(__file__)+"/static/uploads/"+file, 'wb+') as destination:
								for chunk in myfile.chunks():
									destination.write(chunk)
							
							data_s = check_data(file)
							
							if data_s[0]:
								dr = write_data_to_db(data_s[1])
								
								if dr[0]:
									data["msg"] = dr[1]
									return render(request,'portal/import.html',data)
									
								data["msg"] = dr[1]
								data["error"] = 1
								return render(request,'portal/import.html',data)	
							else:
								data["msg"] = data_s[1]
								data["error"] = 1
								return render(request,'portal/import.html',data)
						else:
							
							with open(os.path.dirname(__file__)+"/static/uploads/"+file, 'wb+') as destination:
								for chunk in myfile.chunks():
									destination.write(chunk)
									
							data_s = check_data(file)
							
							if data_s[0]:
								dr = write_data_to_db(data_s[1])
								if dr[0]:
									data["msg"] = dr[1]
									return render(request,'portal/import.html',data)
									
								data["msg"] = dr[1]
								data["error"] = 1
								return render(request,'portal/import.html',data)	
							else:	
								data["msg"] = data_s[1]
								data["error"] = 1
								return render(request,'portal/import.html',data)
					else:
						data["msg"] = "Not a valid filetype"
						data["error"] = 1
						return render(request,'portal/import.html',data)
				else:
					return render(request,'portal/import.html',data)
			return HttpResponse(status=404)	
		return HttpResponse(status=404)	
	return HttpResponse(status=503)	
		

	
	
#===================================================================================
# Location Selects
#===================================================================================	

def permission_location_select(request):
	if restrict_access(request.META['REMOTE_ADDR']):
		servers = location_select(json.loads(request.POST["selectednumbers"]))
		user_id = request.POST["id_user"]
		
		permission = Permissions.objects.filter(user_id = int(user_id)).values_list('server', flat=True)
		
		# Append location names to servers
		for i in range(0,len(servers)):
			try:
				location = Location_tbl.objects.get(pk = int(servers[i]["location_id"]));
				location_name = location.name
			except Location_tbl.DoesNotExist:
				location_name = ""
				
			servers[i]["location_name"] = location_name
			
			if servers[i]["id"] in list(permission):
				servers[i]["selected"] = 1
			else:
				servers[i]["selected"] = 0
				
		return HttpResponse(json.dumps(list(servers), cls=DjangoJSONEncoder))
	return HttpResponse(status=503)	
	
	
#===================================================================================
# GET MORE SERVER DETAILS
#===================================================================================	

def get_more_details(request):
	if restrict_access(request.META['REMOTE_ADDR']):
		if 'logged_in' in request.session:
			if request.session['logged_in'] == True:
				try:
					server = Server_tbl.objects.filter(pk = request.POST["ref_id"]).values('os', 'ram', 'cpu', 'installed_softwares', 'global_ip', 'server_name', 'server_details')
					return HttpResponse(json.dumps(list(server), cls=DjangoJSONEncoder))	
				except Server_tbl.DoesNotExist:
					return HttpResponse(status=500)	
			return HttpResponse(status=404)	
		return HttpResponse(status=404)	
	return HttpResponse(status=503)	
	
	
#===================================================================================
# REPORTS
#===================================================================================		

def reports(request):
	if restrict_access(request.META['REMOTE_ADDR']):
		if 'logged_in' in request.session:
			if request.session['logged_in'] == True:
			
				data = dict({
					'name' : request.session["firstname"].title()+" "+request.session["lastname"].title(),
					'email' : request.session["email"],
					'msg' : "",
					'error' : 0,
					'location_details': request.session['location_details'],
				})
				
				if request.POST:
					output = request.POST["output"]
					column_names_beautify = int(request.POST["column_names_beautify"])
					column_names = request.POST.getlist("column_names")
					location = request.POST.getlist("locations")
					
					# header dictionary
					header_dict = {
						'ipaddress' : 'Asset Name',
						'serial_number' : 'Serial Number',
						'model_number' : 'Model Number',
						'warranty' : 'Warranty',
						'admin_uid' : 'Admin Username',
						'category__name' : 'Category',
						'location__name' : 'Location',
						'os' : 'Operating System',
						'ram' : 'Memory',
						'cpu' : 'CPU',
						'installed_softwares' : 'Installed Softwares',
						'server_name' : 'Asset Name',
						'global_ip' : 'Global IP',
						'server_details' : 'Asset Details',
					}

					new_header = ['id']
					value_list = ['id']

					if len(column_names) > 0:
						if column_names_beautify == 1:
							new_header = ['Asset ID']
							for head in header_dict.keys():
								if head in column_names:
									new_header.append(header_dict[head])
									value_list.append(head)
						else:
							for head in header_dict.keys():
								if head in column_names:
									new_header.append(head)
									value_list.append(head)
					else:
						if column_names_beautify == 1:
							new_header = ['Asset ID']
							for head in header_dict.keys():
								new_header.append(header_dict[head])
								value_list.append(head)
						else:							
							for head in header_dict.keys():
								new_header.append(head)
								value_list.append(head)

					# QUERY SECTION
					#
					server = Server_tbl.objects

					if len(location) > 0:
						server = server.filter(location_id__in = location)
					else:
						server = server.filter(location_id__in = request.session["location_ids"])

					server = server.select_related().values_list(*value_list)

					if output == 'csv':
						rows = [new_header]
						for x in server:
							rows.append(x)

						pseudo_buffer = Echo()
						writer = csv.writer(pseudo_buffer)
						response = StreamingHttpResponse((writer.writerow(row) for row in rows),content_type="text/csv")
						response['Content-Disposition'] = 'attachment; filename="reports.csv"'

					elif output == 'xls':
						workbook = xlwt.Workbook()
						worksheet = workbook.add_sheet('My Worksheet')

						for x in range(len(new_header)):
							worksheet.write(0, x, new_header[x])
						
						row_num = 1
						for row in range(len(server)):
							for col in range(len(server[row])):
								worksheet.write(row_num, col, server[row][col])
							row_num += 1

						response = HttpResponse(content_type='application/ms-excel')
						response['Content-Disposition'] = 'attachment; filename=reports.xls'
						workbook.save(response)
					
					elif output == 'txt':
						rows = [new_header]
						for x in server:
							rows.append(x)

						pseudo_buffer = Echo()
						writer = csv.writer(pseudo_buffer, delimiter ='|',quotechar =',',quoting=csv.QUOTE_MINIMAL)
						response = StreamingHttpResponse((writer.writerow(row) for row in rows),content_type="text/csv")
						response['Content-Disposition'] = 'attachment; filename="reports.txt"'						

					return response
				return render(request,'portal/report.html',data)
			return HttpResponse(status=404)	
		return HttpResponse(status=404)	
	return HttpResponse(status=503)	


#
#
#   DOWNLOAD STREAMING FILE
#
class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

#
#	
#	GET EDIT FORM 
#
def get_edit_form(request):
	if restrict_access(request.META['REMOTE_ADDR']):
		if 'logged_in' in request.session:
			if request.session['logged_in'] == True:
				if request.is_ajax():
					if request.POST:
						id = int(request.POST["ref_id"])		
						try:
							server = Server_tbl.objects.filter(pk = request.POST["ref_id"]).values()
							return HttpResponse(json.dumps(list(server), cls=DjangoJSONEncoder))	
						except Server_tbl.DoesNotExist:
							return HttpResponse(status=500)
					return HttpResponse(status=404)
				return HttpResponse(status=404)
			return HttpResponse(status=404)
		return HttpResponse(status=404)
	return HttpResponse(status=503)

#
#	
#	GET EDIT FORM 
#
def edit_form(request):
	if restrict_access(request.META['REMOTE_ADDR']):
		if 'logged_in' in request.session:
			if request.session['logged_in'] == True:
				if request.is_ajax():
					if request.POST:
						id = int(request.POST["id"])		
						try:
							server = Server_tbl.objects.get(pk = id)

							server.ipaddress = request.POST["ipaddress"]
							server.serial_number = request.POST["serial_number"]
							server.model_number = request.POST["model_number"]
							server.warranty = request.POST["warranty"]
							server.admin_uid = request.POST["username"]
							server.admin_psw = request.POST["password"]
							server.os = request.POST["os"]
							server.cpu = request.POST["cpu"]
							server.ram = request.POST["ram"]
							server.installed_softwares = request.POST["installed_softwares"]
							server.server_name = request.POST["server_name"]
							server.global_ip = request.POST["global_ip"]
							server.server_details = request.POST["server_details"]

							server.save()

							return HttpResponse('1')	
						except Server_tbl.DoesNotExist:
							return HttpResponse(status=500)
					return HttpResponse(status=404)
				return HttpResponse(status=404)
			return HttpResponse(status=404)
		return HttpResponse(status=404)
	return HttpResponse(status=503)