from django.db import models
from django.db.models import Model
from django.conf import settings
import _models

#from _models.product import Product, ProductRegistry


# this function from ice takes a package, then uses pkgutil to import each submodule.
# It then returns a list of types which are subclasses of kls from those submodules.
def TypesFromModule(package, kls):
    import pkgutil
    prefix = package.__name__ + '.'
    found = []
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix):
        last_modname = modname.split('.')[-1]

        module = __import__(modname, fromlist="dummy")

        for k, v in module.__dict__.items():
            if isinstance(v, type):
                if issubclass(v, kls) and not v is kls:
                    if v not in found:
                        found.append(v)

    return found


# Get all the subclasses of Model, because these need to be imported into this
# module's namespace (because django looks in each apps models.py)
types = TypesFromModule(_models, models.Model)

# Register each of those into this module.
for kls in types:
    if Model in kls.__mro__:
        locals()[kls.__name__] = kls

