from django.contrib import admin
from django.db.models import Model

# Register your models here.
import models as mymodels

to_register = []

for n in dir(mymodels):
    #print "checking ", n
    m = getattr(mymodels, n, None)
    if isinstance(m, type) and issubclass(m, Model) and m is not Model:
        if hasattr(m, '_meta') and getattr(m._meta, 'abstract', None):
            continue
        to_register.append(m)

for m in list(set(to_register)):
    if m not in admin.site._registry:
        admin.site.register(m)
