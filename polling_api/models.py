from django.db import models

class Poll(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, editable=False)
    pub_date = models.DateTimeField(auto_now=True, editable=False)
    expire_date = models.DateTimeField()

    def __str__(self):
        return self.title

class Option(models.Model):
    id = models.AutoField(primary_key=True)
    poll = models.ForeignKey(Poll, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

class Vote(models.Model):
    id = models.AutoField(primary_key=True)
    poll = models.ForeignKey(Poll, related_name='votes', on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now=True, editable=False)
    voted_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True)
    ip_hash = models.CharField(max_length=255, null=True)
    session_id = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.voted_by} voted for {self.option} in {self.poll}"