# Quick Reference Guide - GyanUday Improvements

## 🎯 QUICK LINKS

| Feature | File | Usage |
|---------|------|-------|
| Dark Mode | `static/js/ux-enhancements.js` | `new DarkModeToggle()` |
| Notifications | `static/js/ux-enhancements.js` | `window.toast.success()` |
| Form Validation | `static/js/ux-enhancements.js` | Auto-applied to forms |
| GPA Calculator | `accounts/utils.py` | `GPACalculator.calculate_cgpa(student)` |
| Attendance Stats | `accounts/utils.py` | `AttendanceAnalytics.get_attendance_statistics()` |
| Export Data | `accounts/utils.py` | `ExportManager.export_students_csv()` |
| Audit Logs | `accounts/utils.py` | `log_audit(user, action, module)` |
| Notifications API | `dashboard/api_views.py` | `NotificationViewSet` |
| Leave Management | `dashboard/api_views.py` | `LeaveViewSet` |

---

## 🎨 CSS CLASSES

### Animations
```css
.slideIn     /* Slide in animation */
.fadeIn      /* Fade in animation */
.pulse       /* Pulsing effect */
.spin        /* Spinning animation */
```

### Components
```css
.toast              /* Toast notification */
.modal              /* Modal dialog */
.dropdown           /* Dropdown menu */
.breadcrumbs        /* Breadcrumb trail */
.search-box         /* Search input */
.skeleton           /* Loading skeleton */
.badge              /* Status badge */
.progress-bar       /* Progress indicator */
.empty-state        /* Empty state message */
.tooltip            /* Tooltip */
.status-indicator   /* Status dot */
```

### Forms
```css
.form-input      /* Text input */
.form-error      /* Error message */
.form-success    /* Success message */
.form-help       /* Help text */
```

### Dark Mode
```css
/* Automatically applied */
body.dark-mode   /* Dark theme active */
```

---

## 🔧 JAVASCRIPT APIs

### Toast Manager
```javascript
window.toast.success(message, duration)   // Success notification
window.toast.error(message, duration)     // Error notification
window.toast.warning(message, duration)   // Warning notification
window.toast.info(message, duration)      // Info notification
```

### Dark Mode
```javascript
const darkMode = new DarkModeToggle();
darkMode.toggle()              // Toggle dark mode
darkMode.setTheme(true)        // Enable dark mode
darkMode.setTheme(false)       // Disable dark mode
```

### Form Validation
```javascript
// Auto-initialized on all forms
const validator = new FormValidator(form);
validator.validate(event)      // Validate on submit
```

### Table Search
```javascript
new TableSearch(tableSelector, searchSelector);
// Automatically filters table rows
```

### Modal
```javascript
new Modal(modalElement);
modal.open()                   // Open modal
modal.close()                  // Close modal
modal.toggle()                 // Toggle modal
```

### Dropdown
```javascript
new DropdownMenu(trigger, menu);
dropdown.open()                // Open dropdown
dropdown.close()               // Close dropdown
dropdown.toggle()              // Toggle dropdown
```

---

## 🐍 PYTHON UTILITIES

### GPA Calculator
```python
from accounts.utils import GPACalculator

GPACalculator.calculate_cgpa(student)
GPACalculator.calculate_semester_gpa(student, semester)
GPACalculator.calculate_course_gpa(marks_list)
```

### Attendance Analytics
```python
from accounts.utils import AttendanceAnalytics

AttendanceAnalytics.get_student_attendance_trend(student, days=30)
AttendanceAnalytics.get_low_attendance_students(threshold=75)
AttendanceAnalytics.get_attendance_statistics(course=None)
```

### Export Manager
```python
from accounts.utils import ExportManager

ExportManager.export_to_csv(queryset, fields, filename)
ExportManager.export_students_csv(queryset)
ExportManager.export_marks_csv(exam)
ExportManager.export_to_pdf(data, filename, title)
```

### Email Notifications
```python
from accounts.utils import EmailNotificationManager

EmailNotificationManager.notify_low_attendance(student, percentage, threshold)
EmailNotificationManager.notify_fee_due(student, amount, due_date)
EmailNotificationManager.notify_exam_result(student, exam, marks, grade)
```

### Audit Logging
```python
from accounts.utils import log_audit

log_audit(user, action, module, object_id, object_name, changes, request)
```

---

## 🔌 API ENDPOINTS

### Notifications
```
GET    /api/v2/notifications/           # List notifications
GET    /api/v2/notifications/{id}/      # Get notification
POST   /api/v2/notifications/{id}/mark_as_read/
POST   /api/v2/notifications/mark_all_as_read/
GET    /api/v2/notifications/unread_count/
```

### Timetable
```
GET    /api/v2/timetable/               # List all
GET    /api/v2/timetable/my_timetable/  # User's timetable
```

### Holidays
```
GET    /api/v2/holidays/                # List all
```

### Leaves
```
GET    /api/v2/leaves/                  # List user's leaves
POST   /api/v2/leaves/                  # Create leave request
GET    /api/v2/leaves/{id}/             # Get leave details
PATCH  /api/v2/leaves/{id}/             # Update leave
POST   /api/v2/leaves/{id}/approve/     # Approve (faculty)
POST   /api/v2/leaves/{id}/reject/      # Reject (faculty)
```

### Analytics
```
GET    /api/v2/analytics/gpa/           # Get CGPA
GET    /api/v2/analytics/gpa/{id}/      # Get student CGPA
GET    /api/v2/analytics/attendance/    # Overall stats
GET    /api/v2/analytics/low-attendance/ # Low attendance list
GET    /api/v2/export/students/         # Export students CSV
```

### Audit Logs
```
GET    /api/v2/audit-logs/              # List all (admin)
GET    /api/v2/audit-logs/{id}/         # Get log
```

---

## 📋 DATABASE MODELS

### Notification
```python
Notification(
    user,                    # ForeignKey(User)
    title,                   # CharField
    message,                 # TextField
    notification_type,       # CharField (choices)
    is_read,                 # BooleanField
    link,                    # CharField (optional)
    created_at,              # DateTimeField (auto)
)
```

### AuditLog
```python
AuditLog(
    user,                    # ForeignKey(User, nullable)
    action,                  # CharField (choices)
    module,                  # CharField
    object_id,               # IntegerField (optional)
    object_name,             # CharField
    changes,                 # JSONField
    ip_address,              # GenericIPAddressField
    user_agent,              # TextField
    created_at,              # DateTimeField (auto)
)
```

### Timetable
```python
Timetable(
    department,              # ForeignKey(Department)
    course,                  # ForeignKey(Course)
    faculty,                 # ForeignKey(User, nullable)
    day,                     # CharField (choices)
    start_time,              # TimeField
    end_time,                # TimeField
    room_number,             # CharField
    semester,                # IntegerField
    is_active,               # BooleanField
    created_at,              # DateTimeField (auto)
)
```

### Leave
```python
Leave(
    student,                 # ForeignKey(Student)
    leave_type,              # CharField (choices)
    start_date,              # DateField
    end_date,                # DateField
    reason,                  # TextField
    status,                  # CharField (choices)
    approved_by,             # ForeignKey(User, nullable)
    approval_notes,          # TextField
    documents,               # FileField (optional)
    created_at,              # DateTimeField (auto)
)
```

---

## 🎛️ CONFIGURATION

### Enable PDF Export
```bash
pip install reportlab
```

### Configure Email
In `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@gyanuday.edu'
```

### Add to Installed Apps
```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'django_filters',
]
```

---

## 🧪 TESTING EXAMPLES

### Test Toast Notification
```javascript
// In browser console
window.toast.success('Test successful!');
window.toast.error('Test error!');
```

### Test Dark Mode
```javascript
// In browser console
const dm = new DarkModeToggle();
dm.setTheme(true);  // Enable
dm.setTheme(false); // Disable
```

### Test API Endpoint
```bash
# Get CGPA
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v2/analytics/gpa/

# Get timetable
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v2/timetable/my_timetable/

# Export students
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v2/export/students/ > students.csv
```

### Test Backend Utility
```python
# In Django shell: python manage.py shell
from accounts.utils import GPACalculator
from students.models import Student

student = Student.objects.first()
cgpa = GPACalculator.calculate_cgpa(student)
print(f"CGPA: {cgpa}")
```

---

## 🚀 DEPLOYMENT CHECKLIST

- [ ] Run migrations: `python manage.py migrate`
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Update environment variables
- [ ] Configure email settings
- [ ] Set DEBUG = False
- [ ] Configure ALLOWED_HOSTS
- [ ] Set SECRET_KEY from environment
- [ ] Run tests: `python manage.py test`
- [ ] Check logs for errors
- [ ] Verify APIs are accessible
- [ ] Test dark mode toggle
- [ ] Test form validation
- [ ] Create admin user

---

## 📞 KEYBOARD SHORTCUTS

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` | Focus search box |
| `Escape` | Close modal/dropdown |
| `Ctrl+Shift+P` | Command palette (future) |

---

## 🎓 LEARNING PATH

1. **Frontend Basics** → Dark Mode & Animations
2. **User Feedback** → Toasts & Validation  
3. **Navigation** → Breadcrumbs & Menus
4. **Accessibility** → Screen readers & Keyboard nav
5. **Backend Basics** → Models & Utilities
6. **Notifications** → Email & In-app
7. **Analytics** → GPA & Attendance
8. **APIs** → REST endpoints
9. **Deployment** → Production setup

---

## 💡 PRO TIPS

1. **Use `window.toast` globally** - Available after page load
2. **Check browser console** - Errors logged automatically
3. **Use DevTools Network tab** - Debug API calls
4. **Dark mode persists** - Uses localStorage automatically
5. **Validation is automatic** - No extra setup needed
6. **APIs are paginated** - Check response headers
7. **Search is case-insensitive** - Use any case
8. **Animations respect prefers-reduced-motion** - Accessibility first!

---

## 📱 RESPONSIVE BREAKPOINTS

| Device | Width | Sidebar |
|--------|-------|---------|
| Mobile | <480px | Icon-only |
| Tablet | 480-768px | Narrow |
| Desktop | >1000px | Full |

---

## 🔗 USEFUL LINKS

- [Django Docs](https://docs.djangoproject.com/)
- [DRF Docs](https://www.django-rest-framework.org/)
- [MDN Web Docs](https://developer.mozilla.org/)
- [CSS-Tricks](https://css-tricks.com/)

---

**Quick Reference v2.1**  
Last Updated: May 2025
