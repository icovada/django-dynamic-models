from __future__ import annotations

from typing import TypeVar

from django.db import models

from model_utils.managers import InheritanceQuerySet, InheritanceManagerMixin, InheritanceQuerySetMixin, InheritanceManager

ModelT = TypeVar('ModelT', bound=models.Model, covariant=True)


class FastInheritanceQuerySetMixin(InheritanceQuerySetMixin):
    def select_subclasses(self, *subclasses: str | type[models.Model]) -> InheritanceQuerySet:
        if not subclasses:
            selected_subclasses = [x['target_model_name'] for x in self.values(
                'target_model_name').distinct('target_model_name').order_by('target_model_name')]
        else:
            selected_subclasses = subclasses
        return super().select_subclasses(*selected_subclasses)


class FastInheritanceQuerySet(FastInheritanceQuerySetMixin, InheritanceQuerySet):
    ...


class FastInheritanceManagerMixin(InheritanceManagerMixin):
    _queryset_class = FastInheritanceQuerySet


class FastInheritanceManager(FastInheritanceManagerMixin, InheritanceManager):
    ...
