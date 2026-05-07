from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()


class Notification(models.Model):
    """User notifications for important events"""
    
    TYPE_CHOICES = [
        ('attendance', 'Attendance Alert'),
        ('fee', 'Fee Reminder'),
        ('exam', 'Exam Notification'),
        ('result', 'Result Announcement'),
        ('course', 'Course Update'),
        ('system', 'System Notification'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()


class EmailLog(models.Model):
    """Track all email communications"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ]

    recipient = models.EmailField()
    subject = models.CharField(max_length=200)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.recipient}"

    def send(self):
        """Send the email"""
        try:
            send_mail(
                self.subject,
                self.body,
                settings.DEFAULT_FROM_EMAIL,
                [self.recipient],
                fail_silently=False,
            )
            self.status = 'sent'
            self.sent_at = timezone.now()
        except Exception as e:
            self.status = 'failed'
            self.error_message = str(e)
        self.save()


class AuditLog(models.Model):
    """Track all important actions in the system"""
    
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    module = models.CharField(max_length=50)
    object_id = models.IntegerField(null=True, blank=True)
    object_name = models.CharField(max_length=200, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', 'action']),
            models.Index(fields=['module']),
        ]

    def __str__(self):
        return f"{self.action.upper()} - {self.module} - {self.created_at}"
