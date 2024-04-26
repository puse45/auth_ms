from django.db import models


class BaseModelQuerySet(models.query.QuerySet):
    def archive(self):
        self.update(is_archived=True)

    def archived(self):
        self.update(is_archived=True)

    def active(self):
        return self.filter(is_archived=False)


class BaseManager(models.Manager):
    """
    Manager to enable archiving.
    """

    def get_queryset(self):
        return BaseModelQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_query_set().active()

    def archived(self):
        return self.get_query_set().archived()
