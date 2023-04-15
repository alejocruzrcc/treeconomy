from django.db import models
from accounts.models import Company

# Create your models here.
class CommentCompany(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=50)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    approved_comment = models.BooleanField(default=False)


    def approve(self):
        self.approved_comment = True
        self.save()
    
    

    def __str__(self):
        return self.body