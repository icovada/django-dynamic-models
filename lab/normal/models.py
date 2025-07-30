from django.db import models
from django.db.models import CheckConstraint

from changelog.mixins import ChangeLogMixin

class Cable(ChangeLogMixin, models.Model):
    color = models.CharField(max_length=20)
    side_a = models.ForeignKey(
        'DataSocket', on_delete=models.CASCADE, related_name='+', null=True, blank=False)
    side_b = models.ForeignKey(
        'DataSocket', on_delete=models.CASCADE, related_name='+', null=True, blank=False)

    class Meta:
        constraints = [
            CheckConstraint(
                check=(
                    ~models.Q(side_a=models.F('side_b'))
                ),
                name='no_self_loops'
            ),
        ]
        unique_together = [('side_a', 'side_b')]


class Device(ChangeLogMixin, models.Model):
    name = models.CharField(max_length=30)

    def __str__(self) -> str:
        return self.name


class DataSocket(models.Model):
    virtual = models.BooleanField()
    cable = models.ManyToManyField(
        to='self',
        through=Cable,
        through_fields=("side_a", "side_b"),
        symmetrical=False,
        blank=True
    )
    fkdevice = models.ForeignKey(Device, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=30)

    def save(self, *args, **kwargs) -> None:
        if type(self) == DataSocket:
            raise ValueError("Cannot update a Socket directly")

        return super().save(*args, **kwargs)


class Interface(ChangeLogMixin, DataSocket):

    def __str__(self) -> str:
        return self.name


class Console(ChangeLogMixin, DataSocket):
    bauds = models.IntegerField()


