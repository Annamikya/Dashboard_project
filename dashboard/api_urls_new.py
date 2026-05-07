# API URLs for new features

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from dashboard.api_views import (
    NotificationViewSet,
    AuditLogViewSet,
    TimetableViewSet,
    HolidayViewSet,
    LeaveViewSet,
    gpa_view,
    attendance_analytics_view,
    low_attendance_view,
    export_students_view,
)

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'timetable', TimetableViewSet, basename='timetable')
router.register(r'holidays', HolidayViewSet, basename='holiday')
router.register(r'leaves', LeaveViewSet, basename='leave')

urlpatterns = [
    path('', include(router.urls)),
    path('analytics/gpa/', gpa_view, name='gpa'),
    path('analytics/gpa/<int:student_id>/', gpa_view, name='gpa-student'),
    path('analytics/attendance/', attendance_analytics_view, name='attendance-analytics'),
    path('analytics/low-attendance/', low_attendance_view, name='low-attendance'),
    path('export/students/', export_students_view, name='export-students'),
]
