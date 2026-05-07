"""
GyanUday University - Utility Functions
Provides common functionalities like GPA calculation, export, analytics, etc.
"""

import csv
from datetime import datetime, timedelta
from decimal import Decimal
from django.http import HttpResponse
from django.db.models import Avg, Count, Q
from django.template.loader import render_to_string
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


# ═════════════════════════════════════════════════════════
# GPA CALCULATION
# ═════════════════════════════════════════════════════════

class GPACalculator:
    """Calculate GPA/CGPA for students"""
    
    # Grade points mapping (based on most common 10-point scale)
    GRADE_POINTS = {
        'O': 10,    # Outstanding
        'A+': 9,    # Excellent
        'A': 8,     # Very Good
        'B+': 7,    # Good
        'B': 6,     # Above Average
        'C': 5,     # Average
        'P': 4,     # Pass
        'F': 0,     # Fail
        'AB': 0,    # Absent
    }

    @classmethod
    def calculate_course_gpa(cls, marks_list):
        """Calculate GPA for a single course from marks"""
        if not marks_list:
            return 0
        
        total_points = sum(cls.GRADE_POINTS.get(mark.grade, 0) for mark in marks_list)
        return round(total_points / len(marks_list), 2)

    @classmethod
    def calculate_semester_gpa(cls, student, semester):
        """Calculate GPA for a semester"""
        from results.models import Mark
        
        marks = Mark.objects.filter(
            student=student,
            exam__semester=semester
        ).select_related('exam__course')
        
        if not marks.exists():
            return 0
        
        total_credits = 0
        total_points = 0
        
        for mark in marks:
            credit = mark.exam.course.credits
            grade_point = cls.GRADE_POINTS.get(mark.grade, 0)
            total_credits += credit
            total_points += grade_point * credit
        
        return round(total_points / total_credits, 2) if total_credits > 0 else 0

    @classmethod
    def calculate_cgpa(cls, student):
        """Calculate CGPA (Cumulative GPA) for the student"""
        from results.models import Mark
        
        marks = Mark.objects.filter(student=student).select_related('exam__course')
        
        if not marks.exists():
            return 0
        
        total_credits = 0
        total_points = 0
        
        for mark in marks:
            credit = mark.exam.course.credits
            grade_point = cls.GRADE_POINTS.get(mark.grade, 0)
            total_credits += credit
            total_points += grade_point * credit
        
        return round(total_points / total_credits, 2) if total_credits > 0 else 0


# ═════════════════════════════════════════════════════════
# ATTENDANCE ANALYTICS
# ═════════════════════════════════════════════════════════

class AttendanceAnalytics:
    """Generate attendance analytics and insights"""

    @staticmethod
    def get_student_attendance_trend(student, days=30):
        """Get attendance trend for a student over last N days"""
        from attendance.models import Attendance
        
        cutoff_date = datetime.now().date() - timedelta(days=days)
        
        daily_attendance = Attendance.objects.filter(
            student=student,
            date__gte=cutoff_date
        ).extra(select={'date': 'DATE(date)'}).values('date').annotate(
            present=Count('id', filter=Q(status='present')),
            total=Count('id')
        ).order_by('date')
        
        return list(daily_attendance)

    @staticmethod
    def get_low_attendance_students(threshold=75, semester=None):
        """Get students with attendance below threshold"""
        from students.models import Student
        from attendance.models import Attendance
        
        students_low_att = Student.objects.annotate(
            attendance_percentage=Avg(
                'attendance__status',
                filter=Q(attendance__status__in=['present', 'absent'])
            ) * 100
        ).filter(attendance_percentage__lt=threshold)
        
        if semester:
            students_low_att = students_low_att.filter(semester=semester)
        
        return students_low_att

    @staticmethod
    def get_attendance_statistics(course=None, semester=None):
        """Get overall attendance statistics"""
        from attendance.models import Attendance
        
        query = Attendance.objects.all()
        if course:
            query = query.filter(course=course)
        if semester:
            query = query.filter(student__semester=semester)
        
        total = query.count()
        present = query.filter(status='present').count()
        absent = query.filter(status='absent').count()
        
        return {
            'total': total,
            'present': present,
            'absent': absent,
            'percentage': round((present / total * 100), 2) if total > 0 else 0
        }


# ═════════════════════════════════════════════════════════
# EXPORT UTILITIES
# ═════════════════════════════════════════════════════════

class ExportManager:
    """Handle data export in various formats"""

    @staticmethod
    def export_to_csv(queryset, fields, filename):
        """Export queryset to CSV file"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow(fields)
        
        # Write data
        for obj in queryset:
            row = [getattr(obj, field, '') for field in fields]
            writer.writerow(row)
        
        return response

    @staticmethod
    def export_students_csv(queryset=None):
        """Export students to CSV"""
        if queryset is None:
            from students.models import Student
            queryset = Student.objects.all()
        
        fields = ['roll_number', 'first_name', 'last_name', 'email', 'phone', 'status']
        return ExportManager.export_to_csv(queryset, fields, 'students_export')

    @staticmethod
    def export_marks_csv(exam):
        """Export marks for an exam to CSV"""
        marks = exam.marks.select_related('student')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="marks_{exam.id}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Roll Number', 'Student Name', 'Marks', 'Grade', 'Percentage'])
        
        for mark in marks:
            writer.writerow([
                mark.student.roll_number,
                f"{mark.student.first_name} {mark.student.last_name}",
                mark.marks_obtained,
                mark.grade,
                mark.percentage,
            ])
        
        return response

    @staticmethod
    def export_to_pdf(data, filename, title="Document"):
        """Export data to PDF (requires reportlab)"""
        if not HAS_REPORTLAB:
            raise ImportError("reportlab is required for PDF export. Install with: pip install reportlab")
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
        
        doc = SimpleDocTemplate(response, pagesize=A4)
        story = []
        
        # Add title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#2B5CE6',
            spaceAfter=30,
        )
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Add data table
        if isinstance(data, list) and len(data) > 0:
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), '#2B5CE6'),
                ('TEXTCOLOR', (0, 0), (-1, 0), '#FFFFFF'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), '#F0F0F0'),
                ('GRID', (0, 0), (-1, -1), 1, '#CCCCCC'),
            ]))
            story.append(table)
        
        # Add footer
        story.append(Spacer(1, 0.5*inch))
        footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(f"<i>{footer_text}</i>", styles['Normal']))
        
        doc.build(story)
        return response


# ═════════════════════════════════════════════════════════
# EMAIL NOTIFICATIONS
# ═════════════════════════════════════════════════════════

class EmailNotificationManager:
    """Manage email notifications for various events"""

    @staticmethod
    def notify_low_attendance(student, attendance_percentage, threshold):
        """Notify student about low attendance"""
        from accounts.models import Notification, EmailLog
        
        message = f"Your attendance has dropped to {attendance_percentage}%. Minimum required is {threshold}%."
        
        # Create in-app notification
        Notification.objects.create(
            user=student.user,
            title="Low Attendance Alert",
            message=message,
            notification_type='attendance',
            link=f'/attendance/'
        )
        
        # Send email
        if student.email:
            EmailLog.objects.create(
                recipient=student.email,
                subject="Attendance Alert - GyanUday University",
                body=f"""Dear {student.first_name},

{message}

Please contact your department office for more details.

Best regards,
GyanUday University
"""
            ).send()

    @staticmethod
    def notify_fee_due(student, amount_due, due_date):
        """Notify student about fee dues"""
        from accounts.models import Notification, EmailLog
        
        message = f"Fee payment of ₹{amount_due} is due by {due_date}."
        
        Notification.objects.create(
            user=student.user,
            title="Fee Reminder",
            message=message,
            notification_type='fee',
            link=f'/fees/'
        )
        
        if student.email:
            EmailLog.objects.create(
                recipient=student.email,
                subject="Fee Payment Reminder - GyanUday University",
                body=f"""Dear {student.first_name},

{message}

Please make the payment through the fee portal or contact the finance office.

Best regards,
GyanUday University
"""
            ).send()

    @staticmethod
    def notify_exam_result(student, exam, marks, grade):
        """Notify student about exam results"""
        from accounts.models import Notification, EmailLog
        
        message = f"Results for {exam.name} published. Your marks: {marks} (Grade: {grade})"
        
        Notification.objects.create(
            user=student.user,
            title="Result Announcement",
            message=message,
            notification_type='result',
            link=f'/results/'
        )
        
        if student.email:
            EmailLog.objects.create(
                recipient=student.email,
                subject=f"Exam Results - {exam.name}",
                body=f"""Dear {student.first_name},

Results for {exam.name} have been published.

Your Performance:
- Marks: {marks}
- Grade: {grade}
- Course: {exam.course.name}

View detailed report on the student portal.

Best regards,
GyanUday University
"""
            ).send()


# ═════════════════════════════════════════════════════════
# AUDIT LOG HELPER
# ═════════════════════════════════════════════════════════

def log_audit(user, action, module, object_id=None, object_name=None, changes=None, request=None):
    """Log an audit event"""
    from accounts.models import AuditLog
    
    ip_address = None
    user_agent = None
    
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    AuditLog.objects.create(
        user=user,
        action=action,
        module=module,
        object_id=object_id,
        object_name=object_name,
        changes=changes or {},
        ip_address=ip_address,
        user_agent=user_agent,
    )
