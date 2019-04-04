from django.contrib.auth.models import User
from django.db import models
from django.utils.html import *

# Create your models here.


#===================================================================================
# Location_tbl
#===================================================================================

class Location_tbl(models.Model):
	ACTIVE = 1
	INACTIVE = 0
	
	ACTIVE_INACTIVE = ((ACTIVE,"Active"),(INACTIVE, "In-Active"),)
	name = models.CharField(max_length=100, null = True, blank = True, db_index = True,)
	status = models.IntegerField(choices = ACTIVE_INACTIVE, default = ACTIVE, db_index = True,)
	inserted_date = models.DateTimeField(auto_now_add = True, auto_now = False,)
	
	def __str__(self):
		return self.name
	
	class Meta:
		db_table = "location_tbl"
		ordering = ["pk"]
		verbose_name_plural = "Location Table"

#===================================================================================
# Signin_tbl
#===================================================================================	
	
class Signin_tbl(models.Model):
	ACTIVE = 1
	INACTIVE = 0
	
	ACTIVE_INACTIVE = ((ACTIVE,"Active"),(INACTIVE, "In-Active"),)
	ADMIN_STAFF = ((ACTIVE,"Admin"),(INACTIVE, "Staff"),)

	username = models.CharField(max_length=50, null = False, blank = False, db_index = True, unique = True)
	password = models.CharField(max_length=50, null = False, blank = False, db_index = True,)
	usertype = models.IntegerField(choices = ADMIN_STAFF, default = INACTIVE, db_index = True,)
	firstname = models.CharField(max_length=100, null = True, blank = True, db_index = True,)
	lastname = models.CharField(max_length=100, null = True, blank = True, db_index = True,)
	email = models.CharField(max_length=100, null = True, blank = True, db_index = True,)
	status = models.IntegerField(choices = ACTIVE_INACTIVE, default = ACTIVE, db_index = True,)
	location = models.ManyToManyField(Location_tbl, null = True, blank = True,)
	inserted_date = models.DateTimeField(auto_now_add = True, auto_now = False,)	
	
	def __str__(self):
		return self.username
		
	def assigned_locations(self):
		return ', '.join([p.name for p in self.location.all()])
	
	class Meta:
		db_table = "signin"
		ordering = ["pk"]
		verbose_name_plural = "Signin Table"
	
	
#===================================================================================
# Category_tbl
#===================================================================================
	
class Category_tbl(models.Model):
	ACTIVE = 1
	INACTIVE = 0
	
	ACTIVE_INACTIVE = ((ACTIVE,"Active"),(INACTIVE, "In-Active"),)
	
	name = models.CharField(max_length=50, null = False, blank = False, db_index = True, unique = True)
	status = models.IntegerField(choices = ACTIVE_INACTIVE, default = ACTIVE, db_index = True,)
	inserted_date = models.DateTimeField(auto_now_add = True, auto_now = False,)
	
	def __str__(self):
		return self.name
	
	class Meta:
		db_table = "category_tbl"
		ordering = ["pk"]
		verbose_name_plural = "Category Table"	

		
#===================================================================================
# Server_tbl
#===================================================================================		
		
class Server_tbl(models.Model):
	ACTIVE = 1
	INACTIVE = 0
	
	ACTIVE_INACTIVE = ((ACTIVE,"Active"),(INACTIVE, "In-Active"),)
	
	ipaddress = models.CharField(max_length=50, null = False, blank = False, db_index = True, unique = True)
	category = models.ForeignKey(Category_tbl, blank = True,  on_delete=models.CASCADE,)
	serial_number = models.CharField(max_length=100, null = True, blank = True, db_index = True,)
	model_number = models.CharField(max_length=100, null = True, blank = True, db_index = True,)
	location = models.ForeignKey(Location_tbl, null = True, blank = True, on_delete=models.SET_NULL,)
	warranty = models.CharField(max_length=100, null = True, blank = True, db_index = True,)
	admin_uid	= models.CharField(max_length=50, null = True, blank = True, db_index = True,)
	admin_psw = models.CharField(max_length=50, null = True, blank = True, db_index = True,)
	status = models.IntegerField(choices = ACTIVE_INACTIVE, default = ACTIVE, db_index = True,)
	os = models.CharField(max_length=250, null = True, blank = True,)
	ram = models.CharField(max_length=20, null = True, blank = True,)
	cpu = models.CharField(max_length=250, null = True, blank = True,)
	installed_softwares = models.TextField(blank = True,)
	server_name = models.CharField(max_length=250, null = True, blank = True,)
	global_ip = models.CharField(max_length=20, null = True, blank = True,)
	server_details = models.TextField(blank = True,)	
	inserted_date = models.DateTimeField(auto_now_add = True, auto_now = False,)	
	
	def __str__(self):
		return self.ipaddress
		
	class Meta:
		db_table = "server_tbl"
		ordering = ["pk"]
		verbose_name_plural = "Server Table"		
		
#===================================================================================
# Permissions Tbl
#===================================================================================
		
class Permissions(models.Model):
		AUTHORIZED = 1
		UNAUTHORIZED = 0
		
		AUTHORIZED_UNAUTHORIZED = ((AUTHORIZED,"Authorized"),(UNAUTHORIZED, "Un-Authorized"),)
		
		user = models.ForeignKey(Signin_tbl, null = True, blank = True, db_index = True,  on_delete=models.CASCADE,)
		location = models.ManyToManyField(Location_tbl, null = True, blank = True, db_index = True,)
		server = models.ManyToManyField(Server_tbl, null = True, blank = True, db_index = True, )
		permission = models.IntegerField(choices = AUTHORIZED_UNAUTHORIZED, default = UNAUTHORIZED, db_index = True, )
		inserted_date = models.DateTimeField(auto_now_add = True, auto_now = False,)
		
		def access_list(self):
			#location_s = [L.id for L in self.location.all()]
			server_s = [(S.ipaddress, S.location.name) for S in self.server.all()]
			
			data = list()
			for s in server_s:
				data.append(s[0]+" - "+s[1])
			
			return format_html("%s" %(', <br>'.join(data)))
					
									
		class Meta:
			db_table = "permission_tbl"
			ordering = ["pk"]
			verbose_name_plural = "Permission Table"	
