import datetime
import peewee as pw

from iwallpaper.config import CONFIG


class BaseModel(pw.Model):
    class Meta:
        database = CONFIG.db


class Image(BaseModel):
    hashsum = pw.CharField(unique=True, index=True)
    url = pw.CharField(unique=True)
    rank = pw.IntegerField()  # {0, 1, 2, 3, 4, 5}
    filetype = pw.CharField()  # {jpg, png...}
    is_deleted = pw.BooleanField(default=False)
    created_at = pw.DateTimeField(default=datetime.datetime.now)
    updated_at = pw.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return 'Image {{id: {}, hashsum: {}, url: {}, rank: {}, filetype: {}, is_deleted: {}, created_at: {}, updated_at: {}}}'.format(
            self.id, self.hashsum, self.url, self.rank, self.filetype,
            self.is_deleted, self.created_at, self.updated_at)
