from django.db import models
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.apps import apps
from threading import local
from django.contrib import admin


_thread_local = local()


class ChangeLogMixin(models.Model):
    """
    Mixin to add change logging functionality to any model.
    This will create a proper foreign key relationship to ChangeLog.
    """

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Store the class for later processing
        if not hasattr(cls, '_changelog_setup_done'):
            cls._changelog_setup_done = False

        # Connect signals immediately (they don't need the relationship model)
        cls._connect_signals()

    @classmethod
    def _ensure_changelog_setup(cls):
        """
        Ensure the changelog relationship is set up.
        This is called lazily when needed.
        """
        if cls._changelog_setup_done:
            return

        # Create the relationship model
        cls._create_changelog_relationship()
        cls._changelog_setup_done = True

    @classmethod
    def _create_changelog_relationship(cls):
        """
        Dynamically create a model that links this model to ChangeLog
        """
        # Create the relationship model name
        rel_model_name = f"{cls.__name__}ChangeLog"

        # Check if the model already exists
        try:
            existing_model = apps.get_model(
                cls._meta.app_label, rel_model_name)
            cls._changelog_rel_model = existing_model
            return
        except LookupError:
            pass

        # Import ChangeLog here to avoid circular imports
        from .models import ChangeLog

        # Create the relationship model
        attrs = {
            '__module__': cls.__module__,
            'Meta': type('Meta', (), {
                'app_label': cls._meta.app_label,
            }),
            cls.__name__.lower(): models.ForeignKey(
                cls,
                on_delete=models.CASCADE,
                related_name='change_logs'
            ),
            'target_uuid': models.UUIDField(), # needed to we can keep the information after deletion
            'changelog': models.ForeignKey(
                ChangeLog,
                on_delete=models.CASCADE,
                related_name=f'{cls.__name__.lower()}_relations'
            ),
        }

        rel_model = type(rel_model_name, (models.Model,), attrs)
        admin.site.register(rel_model)

        # Store reference to the relationship model
        cls._changelog_rel_model = rel_model

    @classmethod
    def _get_changelog_rel_model(cls):
        """Get the changelog relationship model, creating it if necessary"""
        if not hasattr(cls, '_changelog_rel_model'):
            cls._ensure_changelog_setup()
        return cls._changelog_rel_model

    @classmethod
    def _connect_signals(cls):
        """Connect the change tracking signals"""

        @receiver(pre_save, sender=cls, weak=False)
        def pre_save_handler(sender, instance, **kwargs):
            if instance.pk:
                try:
                    _thread_local.old_instance = sender.objects.get(
                        pk=instance.pk)
                except sender.DoesNotExist:
                    _thread_local.old_instance = None
            else:
                _thread_local.old_instance = None

        @receiver(post_save, sender=cls, weak=False)
        def post_save_handler(sender, instance, created, **kwargs):
            from .models import ChangeLog

            # Get user from thread local if available
            user = getattr(_thread_local, 'user', None)
            old_instance = getattr(_thread_local, 'old_instance', None)

            if created:
                action = 'CREATE'
                old_values = None
                new_values = cls._serialize_instance(instance)
                changed_fields = None
            else:
                action = 'UPDATE'
                old_values = cls._serialize_instance(
                    old_instance) if old_instance else None
                new_values = cls._serialize_instance(instance)
                changed_fields = cls._get_changed_fields(
                    old_instance, instance)

            # Create the ChangeLog entry
            changelog = ChangeLog.objects.create(
                action=action,
                user=user,
                old_values=old_values,
                new_values=new_values,
                changed_fields=changed_fields
            )

            # Get the relationship model and create the relationship
            rel_model = cls._get_changelog_rel_model()
            rel_model.objects.create(
                **{
                    cls.__name__.lower(): instance,
                    'changelog': changelog,
                    'target_uuid': instance.id
                }
            )

        @receiver(post_delete, sender=cls, weak=False)
        def post_delete_handler(sender, instance, **kwargs):
            from .models import ChangeLog

            user = getattr(_thread_local, 'user', None)

            # Create the ChangeLog entry for deletion
            changelog = ChangeLog.objects.create(
                action='DELETE',
                user=user,
                old_values=cls._serialize_instance(instance),
                new_values=None,
                changed_fields=None
            )

            # Note: The relationship will be deleted automatically due to CASCADE

    @classmethod
    def _serialize_instance(cls, instance):
        """Serialize model instance to JSON-compatible dict"""
        if not instance:
            return None

        data = {}
        for field in instance._meta.fields:
            value = getattr(instance, field.name)

            # Handle different field types
            if isinstance(field, models.DateTimeField) and value:
                data[field.name] = value.isoformat()
            elif isinstance(field, models.UUIDField) and value:
                data[field.name] = str(value)
            elif isinstance(field, models.ForeignKey) and value:
                data[field.name] = str(value.pk)
            elif hasattr(value, 'pk'):
                data[field.name] = value.pk
            else:
                data[field.name] = value

        return data

    @classmethod
    def _get_changed_fields(cls, old_instance, new_instance):
        """Get list of changed fields between two instances"""
        if not old_instance:
            return None

        changed = []
        for field in new_instance._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(new_instance, field.name)

            if old_value != new_value:
                changed.append(field.name)

        return changed if changed else None

    def get_change_logs(self):
        """Get all change logs for this instance"""
        rel_model = self.__class__._get_changelog_rel_model()
        relations = rel_model.objects.filter(**{
            self.__class__.__name__.lower(): self
        }).select_related('changelog')
        return [rel.changelog for rel in relations]


# Context manager for setting user in thread local
class ChangeLogContext:
    def __init__(self, user):
        self.user = user

    def __enter__(self):
        _thread_local.user = self.user
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(_thread_local, 'user'):
            delattr(_thread_local, 'user')
