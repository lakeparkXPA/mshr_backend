from admin_api.models import *
import datetime
from django.utils import timezone
def log(request, typ, content):
    """
    Log Type : Log Content
        Log in : Login success, Login fail
        log out : Logout
        Reset password : update password {user_id}
        Add (Student, Health Check-up, School, User, Notice) :
            Insert (Student, Health Check-up, School, User) {id}
        Update (Student, Health Check-up, School, User, Notice) :
            Update (Student, Health Check-up, School, User) {id}
        Update My Info : update information, change password
        Delete (Student, Health Check-up, School, User, Notice) :
            Delete (Student, Health Check-up, School, User) {id}
        Download (Student, Health Check-up) : Download (Student, Health Check-up) file
        Upload Student : Upload Student file
    """

    user_id = request.META.get('HTTP_USER_ID', '')
    user = User.objects.filter(user_id=user_id)
    user_fk = user.values_list('id', flat=True)[0]
    user_name = user.values_list('user_name', flat=True)[0]


    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')


    log_insert = Log()
    log_insert.user_fk = user[0]
    log_insert.user_id = user_id
    log_insert.user_name = user_name
    log_insert.log_type = typ
    log_insert.log_time = timezone.localtime()
    log_insert.log_content = content
    if ip:
        log_insert.ip = ip

    log_insert.save()
