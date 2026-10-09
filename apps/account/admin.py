
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.account.models import CustomerUser

class  UserAdmin(BaseUserAdmin):
    list_display = ( 'email' , 'first_name' , 'last_name', 'phone' , 'is_active' , 'is_staff', 'is_admin', 'is_superuser')
    list_display_links = ( 'email' ,)
    ordering = [ 'date_joined' ]
    search_fields = ( 'email' , 'last_name' , 'phone', )
    readonly_fields = ( 'date_joined' , 'is_superuser' , 'created_at' , 'updated_at', )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_staff=True)

    fieldsets = (
        ( None , { 'fields' : ( 'email' , 'password' )}),
        ( 'Personal Информация' , { 'fields' : ( 'first_name' , 'last_name', 'phone', 'birth_date', 'adress', 'avatar')}),
        ( 'Разрешения' , {
            'fields' : ( 'is_active' , 'is_staff' , 'is_admin' , 'is_superuser' , 'groups' , 'user_permissions')
        }),
        ( 'Важные даты' , {
            'fields' : ( 'date_joined' , 'created_at' , 'updated_at' ,)
        }),
    )

    add_fieldsets = (
        ( None , {
            'classes' : ( 'wide' ,),
            'fields' : (
                'first_name' , 'last_name', 'phone' , 'email' , 'password1' , 'password2' ,
                'is_active' , 'is_staff' , 'is_superuser' , 'is_admin' ,'avatar'
            ),
        }),
    )


admin.site.register(CustomerUser, UserAdmin)