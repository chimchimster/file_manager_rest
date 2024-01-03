from django.db import models
from django.utils.timezone import now


class Storage(models.Model):

    STATUSES = ('R', 'ready'), ('E', 'error'), ('P', 'In progress')

    file_id = models.AutoField(primary_key=True, db_column='pk')
    file_uuid = models.UUIDField(null=False)
    status = models.CharField(max_length=1, choices=STATUSES, default='P')
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    def __str__(self):
        return 'File №%s' % self.file_id


class UserFile(models.Model):

    user_id = models.IntegerField()
    file_id = models.ForeignKey(Storage, on_delete=models.CASCADE, related_name='files')

    def __str__(self):
        return 'User %s, %s' % (self.user_id, self.file_id)
