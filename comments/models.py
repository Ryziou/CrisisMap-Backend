from django.db import models

# Create your models here.
class Comment(models.Model):
    content = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        to='users.User',
        related_name='comments',
        on_delete=models.CASCADE
    )
    event = models.IntegerField(help_text='ReliefWeb event ID')

    def __str__(self):
        return f'Comment {self.id} by {self.author.username} on event {self.event}'