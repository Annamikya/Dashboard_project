"""
GyanUday University - Enhanced API Views
Additional API endpoints for new features
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta

# Import models and serializers
from accounts.models import Notification, AuditLog, User
from results.models import Timetable, Holiday, Leave
from accounts.utils import GPACalculator, AttendanceAnalytics, ExportManager


# ═════════════════════════════════════════════════════════
# SERIALIZERS
# ═════════════════════════════════════════════════════════

from rest_framework import serializers

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'is_read', 'link', 'created_at']
        read_only_fields = ['created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'user_name', 'action', 'module', 'object_name', 'created_at']
        read_only_fields = ['created_at']


class TimetableSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.get_full_name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    
    class Meta:
        model = Timetable
        fields = ['id', 'course', 'course_code', 'day', 'start_time', 'end_time', 
                 'room_number', 'faculty', 'faculty_name', 'semester', 'is_active']


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = ['id', 'name', 'start_date', 'end_date', 'description', 
                 'is_institute_holiday', 'departments']


class LeaveSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.first_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = Leave
        fields = ['id', 'student', 'student_name', 'leave_type', 'start_date', 'end_date',
                 'reason', 'status', 'approved_by', 'approved_by_name', 'approval_notes',
                 'duration_days', 'created_at']
        read_only_fields = ['created_at', 'duration_days']


# ═════════════════════════════════════════════════════════
# VIEWSETS
# ═════════════════════════════════════════════════════════

class NotificationViewSet(viewsets.ModelViewSet):
    """Notifications API"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'is_read']
    ordering = ['-created_at']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read"""
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        return Response({'status': 'All notifications marked as read'})

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark single notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'status': 'Notification marked as read'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get unread notification count"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return Response({'unread_count': count})


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Audit logs (admin only)"""
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['action', 'module', 'user']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_admin():
            return AuditLog.objects.all()
        # Non-admins can only see their own logs
        return AuditLog.objects.filter(user=self.request.user)


class TimetableViewSet(viewsets.ReadOnlyModelViewSet):
    """Timetable/Schedule API"""
    serializer_class = TimetableSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['department', 'day', 'semester', 'is_active']
    ordering = ['day', 'start_time']

    def get_queryset(self):
        return Timetable.objects.filter(is_active=True)

    @action(detail=False, methods=['get'])
    def my_timetable(self, request):
        """Get timetable for current user's department"""
        if hasattr(request.user, 'student_profile'):
            timetable = Timetable.objects.filter(
                department=request.user.student_profile.department
            )
        elif hasattr(request.user, 'faculty'):
            timetable = Timetable.objects.filter(faculty=request.user)
        else:
            timetable = Timetable.objects.none()
        
        serializer = self.get_serializer(timetable, many=True)
        return Response(serializer.data)


class HolidayViewSet(viewsets.ReadOnlyModelViewSet):
    """Holiday/Calendar API"""
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['start_date']

    def get_queryset(self):
        user = self.request.user
        holidays = Holiday.objects.filter(is_institute_holiday=True)
        
        # Add department-specific holidays if student
        if hasattr(user, 'student_profile'):
            dept_holidays = Holiday.objects.filter(
                departments=user.student_profile.department
            )
            holidays = holidays | dept_holidays
        
        return holidays.distinct()


class LeaveViewSet(viewsets.ModelViewSet):
    """Leave/Absence management API"""
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'leave_type']
    ordering = ['-start_date']

    def get_queryset(self):
        user = self.request.user
        
        if user.is_faculty():
            # Faculty can see leaves from students in their department
            return Leave.objects.filter(
                student__department__faculty=user
            )
        else:
            # Students can only see their own leaves
            if hasattr(user, 'student_profile'):
                return Leave.objects.filter(student__user=user)
        
        return Leave.objects.none()

    def perform_create(self, serializer):
        """Create leave request"""
        if hasattr(self.request.user, 'student_profile'):
            serializer.save(student=self.request.user.student_profile)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a leave request (faculty only)"""
        if not request.user.is_faculty():
            return Response({'error': 'Only faculty can approve leaves'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        leave = self.get_object()
        leave.status = 'approved'
        leave.approved_by = request.user
        leave.approved_at = timezone.now()
        leave.approval_notes = request.data.get('notes', '')
        leave.save()
        
        serializer = self.get_serializer(leave)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a leave request (faculty only)"""
        if not request.user.is_faculty():
            return Response({'error': 'Only faculty can reject leaves'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        leave = self.get_object()
        leave.status = 'rejected'
        leave.approved_by = request.user
        leave.approval_notes = request.data.get('notes', '')
        leave.save()
        
        serializer = self.get_serializer(leave)
        return Response(serializer.data)


# ═════════════════════════════════════════════════════════
# ANALYTICS VIEWS
# ═════════════════════════════════════════════════════════

from rest_framework.decorators import api_view, permission_classes

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gpa_view(request, student_id=None):
    """Get GPA/CGPA for a student"""
    from students.models import Student
    
    if student_id:
        student = Student.objects.get(pk=student_id)
    elif hasattr(request.user, 'student_profile'):
        student = request.user.student_profile
    else:
        return Response({'error': 'No student profile found'}, status=status.HTTP_400_BAD_REQUEST)
    
    cgpa = GPACalculator.calculate_cgpa(student)
    
    # Get semester-wise GPA
    semester_gpas = []
    for sem in range(1, 9):
        gpa = GPACalculator.calculate_semester_gpa(student, sem)
        if gpa > 0:
            semester_gpas.append({'semester': sem, 'gpa': gpa})
    
    return Response({
        'student': str(student),
        'cgpa': cgpa,
        'semester_gpas': semester_gpas
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_analytics_view(request):
    """Get attendance analytics"""
    analytics = AttendanceAnalytics.get_attendance_statistics()
    return Response(analytics)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def low_attendance_view(request):
    """Get students with low attendance"""
    threshold = request.query_params.get('threshold', 75)
    students = AttendanceAnalytics.get_low_attendance_students(int(threshold))
    
    data = [{
        'name': f"{s.first_name} {s.last_name}",
        'roll_number': s.roll_number,
        'department': s.department.name,
    } for s in students]
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_students_view(request):
    """Export students to CSV"""
    from students.models import Student
    queryset = Student.objects.all()
    return ExportManager.export_students_csv(queryset)
