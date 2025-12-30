import os
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE','routine_planner.settings')
import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from accounts.models import CustomUser
from django.conf import settings
import uuid

# Ensure the test client host is allowed (the test client uses 'testserver')
try:
    if 'testserver' not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ['testserver']
except Exception:
    try:
        settings.ALLOWED_HOSTS = ['testserver']
    except Exception:
        pass

User = get_user_model()

print('Starting admin smoke test')
# ensure a staff user exists (create a temporary superuser if none)
staff = User.objects.filter(is_staff=True).first()
created_temp = False
if not staff:
    staff = User.objects.create_superuser(username='admin_smoke', email='admin_smoke@example.com', password='admin_smoke_pass')
    created_temp = True
    print('Created temporary superuser:', staff.username)

client = Client()
# use force_login to avoid password issues
client.force_login(staff)
print('Force-logged in as', staff.username)

# create a pending user with a unique suffix to avoid collisions
suffix = uuid.uuid4().hex[:6]
username = f'smoke_user_{suffix}'
email = f'smoke_user_{suffix}@example.com'
pending = CustomUser.objects.create_user(username=username, email=email, password='smoke_pass', is_active=False)
print('Created pending user', pending.pk, username)

from django.test import RequestFactory
from accounts import views as account_views

# Call views directly using RequestFactory to avoid client formatting/host issues
rf = RequestFactory()
post_body = json.dumps({'user_id': pending.pk}).encode('utf-8')
req = rf.post('/accounts/admin/reset-password/', data=post_body, content_type='application/json')
req.user = staff
resp = account_views.reset_user_password_view(req)
print('Reset password (direct) status:', getattr(resp, 'status_code', None), getattr(resp, 'content', None)[:500])

req2 = rf.post('/accounts/admin/delete-user/', data=post_body, content_type='application/json')
req2.user = staff
resp2 = account_views.delete_user_view(req2)
print('Delete user (direct) status:', getattr(resp2, 'status_code', None), getattr(resp2, 'content', None)[:500])

# cleanup temporary superuser if we created one
if created_temp:
    staff.delete()
    print('Removed temporary superuser')

print('Smoke test completed')
