from django.test import Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from dashboard.models import DailyRoutine, TaskCategory, Task

User = get_user_model()
# create or reset test user
u, created = User.objects.get_or_create(username='testuser', defaults={'email':'test@example.com'})
if created:
    u.set_password('testpass')
    u.save()
else:
    u.set_password('testpass')
    u.save()

# create category
cat, _ = TaskCategory.objects.get_or_create(name='General', defaults={'color':'#6c757d'})

# create routine for today
today = timezone.now().date()
routine, _ = DailyRoutine.objects.get_or_create(user=u, date=today, defaults={'notes':'smoke test'})

# create a task if none
if routine.tasks.count() == 0:
    Task.objects.create(routine=routine, time='08:00 AM', description='Test task', category=cat, is_completed=False)

client = Client()
logged_in = client.login(username='testuser', password='testpass')
print('login:', logged_in)

urls = ['/', '/accounts/profile/', '/routine/create/', '/history/', '/statistics/', f'/routine/{routine.pk}/', '/admin/']
for url in urls:
    resp = client.get(url)
    print(url, resp.status_code)
    if resp.status_code >= 400:
        print(resp.content[:200])

# anonymous checks
print('\nAnonymous requests:')
client2 = Client()
for url in ['/', '/accounts/profile/', '/routine/create/']:
    resp = client2.get(url)
    print(url, resp.status_code)
    if resp.status_code >= 400:
        print(resp.content[:200])
