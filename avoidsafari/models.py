from django.db import models


# Create your models here.
class Comment(models.Model):
    post_id = models.CharField(max_length=8)
    comment_id = models.CharField(max_length=8, unique=True)
    length = models.IntegerField()
    timestamp = models.DateTimeField()
    
    def __repr__(self):
        return '%s/%s' % (self.post_id, self.comment_id)
    
    def __str__(self):
        return repr(self)
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    def __hash__(self):
        return hash(self.post_id + self.comment_id)