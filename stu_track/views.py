from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Profile,Student,BehaviorLog,Teacher,Attendance,Marks,Notice
from django.utils.crypto import get_random_string
from django.db import IntegrityError
from django.contrib import messages

from django.core.files.storage import FileSystemStorage
from .ml.predictor import predict_behavior
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpResponseForbidden
from functools import wraps



def admin_required(view_func):

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):

        profile = Profile.objects.filter(user=request.user).first()

        if profile is None:
            return HttpResponseForbidden("User profile not found.")

        if profile.role != 'admin':
            return HttpResponseForbidden(
                "You are not authorized to access this page."
            )

        return view_func(request, *args, **kwargs)

    return wrapper





def teacher_required(view_func):

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):

        profile = Profile.objects.filter(user=request.user).first()

        if profile is None:
            return HttpResponseForbidden("User profile not found.")

        if profile.role not in ['teacher', 'admin']:
            return HttpResponseForbidden(
                "You are not authorized to access this page."
            )

        return view_func(request, *args, **kwargs)

    return wrapper





def student_required(view_func):

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):

        profile = Profile.objects.filter(user=request.user).first()

        if profile is None:
            return HttpResponseForbidden("User profile not found.")

        if profile.role != 'student':
            return HttpResponseForbidden(
                "You are not authorized to access this page."
            )

        return view_func(request, *args, **kwargs)

    return wrapper



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']

        user = authenticate(request, username=username, password=password)

        if user:
            profile = Profile.objects.filter(user=user).first()

            if profile is None:
                return render(request, 'login.html', {
        'error': 'User profile not found.'})

            # CHECK ROLE MATCH
            if profile.role != role:
                return render(request, 'login.html', {'error': 'Wrong role selected'})

            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')






def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']

        # Public signup is allowed only for students
        if role != 'student':
            return render(
                request,
                'signup.html',
                {'error': 'Only students can create an account through signup.'}
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                'signup.html',
                {'error': 'Username already exists'}
            )

        user = User.objects.create_user(
            username=username,
            password=password
        )

        Profile.objects.create(
            user=user,
            role='student'
        )

        Student.objects.create(
            user=user,
            roll_number=f"STD{user.id}",
            department="Not Assigned"
        )

        return redirect('login')

    return render(request, 'signup.html')


@login_required
def dashboard_view(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    role = profile.role

    if role == 'student':
        return redirect('student_dashboard')

    elif role == 'teacher':
        return redirect('teacher_dashboard')

    elif role == 'admin':
        return redirect('admin_dashboard')

    else:
        return redirect('logout')


def logout_view(request):
    logout(request)
    return redirect('login')
#=============================Teacher_dashboard=======================================================================



@teacher_required
def update_marks(request):
    if request.method == 'POST':
        student_id = request.POST['student']
        subject = request.POST['subject']
        marks = request.POST['marks']
        Marks.objects.create(student_id=student_id, subject=subject, marks=marks)
    students = Student.objects.all()
    return render(request, 'teacher/update_marks.html', {'students': students})

@teacher_required
def mark_attendance(request):
    if request.method == 'POST':
        student_id = request.POST['student']
        status = request.POST['status']

        try:
            Attendance.objects.create(
                student_id=student_id,
                date=timezone.now().date(),
                status=status
            )

        except IntegrityError:messages.error(request,
        'Attendance has already been marked for this student today.'
    )

    students = Student.objects.all()

    return render(
        request,
        'teacher/mark_attendance.html',
        {'students': students}
    )


@teacher_required
def teacher_view_attendance(request):
    attendance = Attendance.objects.select_related(
        'student'
    ).order_by('-date', 'student__full_name')

    return render(
        request,
        'teacher/attendance.html',
        {
            'attendance': attendance
        }
    )



@teacher_required
def log_behavior(request):
    if request.method == 'POST':
        student_id = request.POST['student']
        activity = request.POST['activity']
        BehaviorLog.objects.create(student_id=student_id, activity=activity)
    students = Student.objects.all()
    return render(request, 'teacher/log_behavior.html', {'students': students})




@teacher_required
def ai_behavior_detection(request):
    prediction = None
    students = Student.objects.all()

    if request.method == 'POST' and request.FILES.get('image'):
        student_id = request.POST['student']
        image_file = request.FILES['image']

        fs = FileSystemStorage()
        filename = fs.save(image_file.name, image_file)
        file_path = fs.path(filename)

        try:
            prediction = predict_behavior(file_path)

            # Save AI result into database
            BehaviorLog.objects.create(
                student_id=student_id,
                activity=prediction
            )

        finally:
            # Delete the uploaded image after prediction
            if fs.exists(filename):
                fs.delete(filename)

    return render(
        request,
        'teacher/ai_behavior.html',
        {'students': students, 'prediction': prediction})

#========================================student_dashboard=======================================================================



@student_required
def student_marks(request):
    student=get_object_or_404(Student, user=request.user)
    marks = Marks.objects.filter(student=student)
    return render(request, 'student/marks.html', {'marks': marks})

@student_required
def student_attendance(request):
    student = get_object_or_404(Student, user=request.user)

    attendance = Attendance.objects.filter(
        student=student
    ).order_by('-date')

    return render(
        request,
        'student/attendance.html',
        {'attendance': attendance}
    )


@student_required
def student_report(request):
    student = get_object_or_404(Student, user=request.user)

    marks = Marks.objects.filter(student=student)

    total_marks = sum(mark.marks for mark in marks)

    total_subjects = marks.count()

    average = total_marks / total_subjects if total_subjects > 0 else 0

    return render(
        request,
        'student/report.html',
        {
            'marks': marks,
            'student': student,
            'total_marks': total_marks,
            'total_subjects': total_subjects,
            'average': average,
        }
    )

@student_required
def student_behavior(request):
    student = get_object_or_404(Student, user=request.user)

    behaviors = BehaviorLog.objects.filter(student=student)

    return render(
        request,
        'student/behaviour.html',
        {'behaviors': behaviors}
    )



#=====================================Admin============================================================

@admin_required
def admin_dashboard(request):

    total_students = Student.objects.count()

    total_teachers = Teacher.objects.count()

    pending_fees = Student.objects.filter(
        fee_status='Unpaid'
    ).count()

    ai_alerts = BehaviorLog.objects.count()

    total_classes = Student.objects.values(
        'department'
    ).distinct().count()

    recent_logs = BehaviorLog.objects.order_by(
        '-timestamp' )[:10]

    attendance_today = Attendance.objects.filter(
        date=timezone.now().date() ).count()

    recent_notices = Notice.objects.order_by('-date')[:3]

    # Get the newly created account credentials
    created_username = request.session.pop('created_username', None)
    created_password = request.session.pop('created_password', None)

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'pending_fees': pending_fees,
        'ai_alerts': ai_alerts,
        'total_classes': total_classes,
        'attendance_today': attendance_today,
        'behavior_logs': recent_logs,
        'notices': recent_notices,
        'created_username': created_username,
        'created_password': created_password,
    }

    return render(
        request,
        'dashboards/admin_dashboard.html',
        context)



@admin_required
def manage_teachers(request):

    teachers = Teacher.objects.all()

    # Get the newly created teacher credentials
    created_username = request.session.pop('created_username', None)
    created_password = request.session.pop('created_password', None)

    context = {
        'teachers': teachers,
        'created_username': created_username,
        'created_password': created_password,
    }

    return render(
        request,
        'admin/teachers.html',
        context
    )


@admin_required
def add_teacher(request):
    if request.method == 'POST':
        username = request.POST['name']
        password=get_random_string(8)

        user = User.objects.create_user(
            username=username,
            password=password
        )

        Profile.objects.create(
            user=user,
            role='teacher'
        )

        Teacher.objects.create(
            user=user,
            teacher_id=request.POST['teacher_id'],
            name=request.POST['name'],
            subject=request.POST['subject'],
            class_assigned=request.POST['class_assigned'],
            salary=request.POST['salary']
        )

        request.session['created_username'] = username
        request.session['created_password'] = password

        return redirect('manage_teachers')

    return render(request, 'admin/add_teacher.html')


@admin_required
def edit_teacher(request, teacher_id):

    teacher = get_object_or_404(Teacher, id=teacher_id)

    if request.method == 'POST':

        teacher.name = request.POST['name']
        teacher.subject = request.POST['subject']
        teacher.class_assigned = request.POST['class_assigned']
        teacher.salary = request.POST['salary']

        teacher.save()

        return redirect('manage_teachers')

    return render(
        request,
        'admin/edit_teacher.html',
        {'teacher': teacher}
    )


@admin_required
def delete_teacher(request, teacher_id):

    teacher = get_object_or_404(Teacher, id=teacher_id)

    teacher.delete()

    return redirect('manage_teachers')




@admin_required
def add_students(request):

    if request.method == 'POST':

        username = request.POST['roll_number']
        password = get_random_string(8)

        user = User.objects.create_user(
            username=username,
            password=password
            
        )
        Profile.objects.create(
            user=user,
            role='student'
        )

        Student.objects.create(
            user=user,
            full_name=request.POST['full_name'],
            mother_name=request.POST['mother_name'],
            father_name=request.POST['father_name'],
            dob=request.POST['dob'],
            roll_number=request.POST['roll_number'],
            department=request.POST['department'],
            fee_status=request.POST['fee_status']
        )
        request.session['created_username'] = username
        request.session['created_password'] = password


        return redirect('admin_dashboard')

    return render(request, 'admin/add_students.html')



@admin_required
def edit_student(request, student_id):

    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':

        student.full_name = request.POST['full_name']
        student.father_name = request.POST['father_name']
        student.mother_name = request.POST['mother_name']
        student.roll_number = request.POST['roll_number']
        student.department = request.POST['department']
        student.fee_status = request.POST['fee_status']
        student.dob = request.POST['dob']

        student.save()

        return redirect('manage_students')

    return render(
        request,
        'admin/edit_student.html',
        {'student': student}
    )






@admin_required
def manage_students(request):

    students = Student.objects.all()

    return render(
        request,
        'admin/students.html',
        {'students': students}
    )


@admin_required
def delete_student(request, student_id):

    student = get_object_or_404(Student, id=student_id)

    student.delete()

    return redirect('manage_students')




@admin_required
def add_notice(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        audience = request.POST['audience']

        Notice.objects.create(
            title=title,
            description=description,
            audience=audience
        )

        return redirect('admin_dashboard')

    return render(request, 'admin/add_notice.html')


@login_required
def notices(request):
    profile = Profile.objects.filter(user=request.user).first()

    if profile is None:
        return HttpResponseForbidden("User profile not found.")

    if profile.role == 'student':
        audience = ['All', 'Students']
    elif profile.role == 'teacher':
        audience = ['All', 'Teachers']
    else:
        audience = ['All']

    notices = Notice.objects.filter(
        audience__in=audience
    ).order_by('-date')

    return render(
        request,
        'notices.html',
        {'notices': notices}
    )



@teacher_required
def teacher_report_cards(request):

    students = Student.objects.all()

    return render(
        request,
        'teacher/report_cards.html',
        {
            'students': students
        }
    )

@teacher_required
def teacher_student_report(request, student_id):

    student = get_object_or_404(Student, id=student_id)

    marks = Marks.objects.filter(student=student)

    total_marks = sum(mark.marks for mark in marks)

    total_subjects = marks.count()

    average = (
        total_marks / total_subjects
        if total_subjects > 0
        else 0
    )

    return render(
        request,
        'student_report.html',
        {
            'student': student,
            'marks': marks,
            'total_marks': total_marks,
            'total_subjects': total_subjects,
            'average': average,
        }
    )



@teacher_required
def teacher_dashboard(request):

    total_students = Student.objects.count()

    attendance_today = Attendance.objects.filter(
        date=timezone.now().date()
    ).count()

    total_marks = Marks.objects.count()

    total_behavior_logs = BehaviorLog.objects.count()

    # Currently all BehaviorLog records are used by the AI system
    ai_detections = BehaviorLog.objects.count()

    # Until we create a separate ReportCard model,
    # students with marks can be considered report-ready
    report_cards = Student.objects.filter(
        marks__isnull=False
    ).distinct().count()

    context = {
        'total_students': total_students,
        'attendance_today': attendance_today,
        'total_marks': total_marks,
        'total_behavior_logs': total_behavior_logs,
        'ai_detections': ai_detections,
        'report_cards': report_cards,
    }

    return render(
        request,
        'dashboards/teacher_dashboard.html',
        context
    )



@student_required
def student_dashboard(request):

    student = get_object_or_404(Student, user=request.user)

    marks = Marks.objects.filter(student=student)

    total_subjects = marks.count()

    total_marks = sum(mark.marks for mark in marks)

    average_marks = (
        total_marks / total_subjects
        if total_subjects > 0
        else 0
    )

    attendance_records = Attendance.objects.filter(
        student=student
    ).count()

    behavior_records = BehaviorLog.objects.filter(
        student=student
    ).count()

    notice_count = Notice.objects.filter(
        audience__in=['All', 'Students']
    ).count()

    context = {
        'student': student,
        'total_subjects': total_subjects,
        'total_marks': total_marks,
        'average_marks': average_marks,
        'attendance_records': attendance_records,
        'behavior_records': behavior_records,
        'notice_count': notice_count,
    }

    return render(
        request,
        'dashboards/student_dashboard.html',
        context
    )