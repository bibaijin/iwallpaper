import peewee as pw

from iwallpaper.config import CONFIG


class BaseModel(pw.Model):
    class Meta:
        database = CONFIG.db


class Image(BaseModel):
    hashsum = pw.CharField(unique=True, index=True)
    url = pw.CharField(unique=True)
    rank = pw.IntegerField()  # {0, 1, 2, 3, 4, 5}
    filetype = pw.CharField()  # jpg/png...

    def __str__(self):
        return 'Image {{hashsum: {}, url: {}, rank: {}, filetype: {}}}'.format(
            self.hashsum, self.url, self.rank, self.filetype)
