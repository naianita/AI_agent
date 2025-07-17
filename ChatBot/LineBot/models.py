from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
import uuid

class UserProfile(models.Model):
    """Extended user profile for chatbot interactions"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    uid = models.CharField(max_length=50, unique=True, validators=[MinLengthValidator(1)])
    name = models.CharField(max_length=255, blank=True)
    pic_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.name} ({self.uid})"

class ChatMessage(models.Model):
    """Model for storing chat messages with better structure"""
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('assistant', 'Assistant Response'),
        ('system', 'System Message'),
        ('note', 'User Note'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='user')
    content = models.TextField(validators=[MinLengthValidator(1)])
    response = models.TextField(blank=True, null=True)  # For assistant responses
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_processed = models.BooleanField(default=False)
    processing_time = models.FloatField(null=True, blank=True)  # Time taken to process in seconds
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_profile', 'created_at']),
            models.Index(fields=['message_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user_profile.name}: {self.content[:50]}..."
    
    @property
    def is_note(self):
        return self.message_type == 'note'

class ConversationSession(models.Model):
    """Model for grouping related messages into conversation sessions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=255, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    message_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'conversation_sessions'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Session {self.id}: {self.title or 'Untitled'}"

class UserNote(models.Model):
    """Dedicated model for user notes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(validators=[MinLengthValidator(1)])
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'user_notes'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title or 'Untitled Note'} - {self.user_profile.name}"

# Legacy model for backward compatibility
class User_Info(models.Model):
    """Legacy model - kept for backward compatibility"""
    uid = models.CharField(max_length=50, null=False, default='')  # user_id
    name = models.CharField(max_length=255, blank=True, null=False)  # LINE名字
    mtext = models.CharField(max_length=255, blank=True, null=False)  # 文字訊息紀錄
    mdt = models.DateTimeField(auto_now=True)  # 儲存的日期時間
    pic_url = models.CharField(max_length=255, blank=True, null=True)  # Profile picture URL
    response = models.CharField(max_length=255, blank=True, null=True)  # Agent's response

    def __str__(self):
        return self.uid

