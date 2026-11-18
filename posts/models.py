from django.db import models
from django.contrib.auth.models import User
class category(models.Model):
    name=models.CharField(max_length=100, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self): 
        return self.name
    
class Tag(models.Model):
    name=models.CharField(max_length=100, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self): 
        return self.name

class BlogPost(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    category = models.ForeignKey(category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    summary = models.TextField(null=True, blank=True)
    def __str__(self): 
        return self.title


class Reaction(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    REACTION_CHOICES = [(LIKE, 'Like'), (DISLIKE, 'Dislike')]

    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        # One reaction per user per post (they can switch like ↔ dislike)
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} – {self.reaction_type} – {self.post.title}"


class Report(models.Model):
    SPAM = 'spam'
    INAPPROPRIATE = 'inappropriate'
    MISINFORMATION = 'misinformation'
    OTHER = 'other'
    REASON_CHOICES = [
        (SPAM, 'Spam'),
        (INAPPROPRIATE, 'Inappropriate Content'),
        (MISINFORMATION, 'Misinformation'),
        (OTHER, 'Other'),
    ]

    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, default=OTHER)
    description = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')   # one report per user per post

    def __str__(self):
        return f"Report by {self.user.username} on {self.post.title}"
    
class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_on']   # newest comments first

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"

class PostImage(models.Model):
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return f"Image for {self.post.title}"