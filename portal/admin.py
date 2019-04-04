from __future__ import unicode_literals
from django.contrib import admin
from .models import Signin_tbl, Category_tbl, Server_tbl, Permissions, Location_tbl
from django import forms

# Register your models here.

class Category_tblAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'status', 'inserted_date') 
	list_display_links = ('id','name',)
	search_fields = ('id', 'name', )
	list_filter = ('status','inserted_date',)
	list_per_page = 50	


class Location_tblAdmin(admin.ModelAdmin):
	list_display = ('id', 'name' ,'inserted_date',) 
	list_display_links = ('id','name', )
	search_fields = ('name',)
	list_filter = ('name', 'inserted_date')
	list_per_page = 50	

	
class Signin_tblAdmin(admin.ModelAdmin):
	list_display = ('id', 'username', 'usertype', 'firstname', 'lastname', 'email', 'status', 'inserted_date', 'assigned_locations') 
	list_display_links = ('id','username',)
	search_fields = ('id', 'username', 'firstname', 'lastname',)
	list_filter = ('status','inserted_date',)
	list_per_page = 50	

	
class Server_tblAdmin(admin.ModelAdmin):
	list_display = ('id', 'ipaddress', 'category', 'serial_number', 'model_number', 'location' , 'warranty', 'admin_uid' , 'admin_psw', 'os', 'ram', 'cpu', 'installed_softwares', 'server_name', 'global_ip', 'server_details', 'inserted_date') 
	list_display_links = ('id','ipaddress',)
	search_fields = ('id', 'ipaddress', )
	list_filter = ('status','inserted_date',)
	list_per_page = 50	
	
	
		
class PermissionsAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'permission', 'access_list') 
	list_display_links = ('id', 'user',)
	search_fields = ('id', 'user',)
	list_filter = ('user' , 'permission' ,'inserted_date',)
	list_per_page = 50	
	
	class Media:
		js = ('custom_js/fkeys.js',)
	
	


# Register your models here.	
admin.site.register(Signin_tbl, Signin_tblAdmin)	
admin.site.register(Category_tbl, Category_tblAdmin)	
admin.site.register(Server_tbl, Server_tblAdmin)	
admin.site.register(Permissions, PermissionsAdmin)
admin.site.register(Location_tbl, Location_tblAdmin)
