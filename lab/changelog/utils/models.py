from django.db.models import Model

from .managers import FastInheritanceManager

class ChangeLoggedModel(Model):
    class Meta:
        abstract = True
        
    objects = FastInheritanceManager()