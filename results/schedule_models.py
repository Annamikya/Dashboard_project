from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import User
from students.models import Department
from courses.models import Course


class Timetable(models.Model):
    """Class schedule/timetable management"""
    
    DAYS = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
    ]

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='timetables')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='timetables')
    faculty = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'faculty'})
    day = models.CharField(max_length=3, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=50, blank=True)
    semester = models.IntegerField(choices=[(i, f'Semester {i}') for i in range(1, 9)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['day', 'start_time']
        unique_together = ('course', 'day', 'start_time', 'semester')
        indexes = [
            models.Index(fields=['department', 'day']),
        ]

    def __str__(self):
        return f"{self.course.name} - {self.get_day_display()} {self.start_time}"

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time")


class Holiday(models.Model):
    """Holiday and vacation management"""
    
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)
    is_institute_holiday = models.BooleanField(default=True, help_text="Applies to entire institute if True")
    departments = models.ManyToManyField(Department, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("Start date must be before end date")


class Leave(models.Model):
    """Student leave/absence management"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    LEAVE_TYPE = [
        ('medical', 'Medical'),
        ('personal', 'Personal'),
        ('emergency', 'Emergency'),
        ('other', 'Other'),
    ]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # For approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='approved_leaves', limit_choices_to={'role': 'faculty'})
    approval_notes = models.TextField(blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    documents = models.FileField(upload_to='leave_documents/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.student.first_name} - {self.leave_type} Leave ({self.start_date})"

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("Start date must be before end date")

    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days + 1
