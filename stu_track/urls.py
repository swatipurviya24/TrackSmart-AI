from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'), 
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    #Teacher dashboard=========================================================
    
    path('teacher/marks/', views.update_marks, name='update_marks'),
    path('teacher/attendance/', views.mark_attendance, name='mark_attendance'),
    path('teacher/behavior/', views.log_behavior, name='log_behavior'),
    
    path('teacher/ai-behavior/', views.ai_behavior_detection, name='ai_behavior'),
    path('teacher/report-cards/',views.teacher_report_cards,name='teacher_report_cards'),

    path('teacher/report-card/<int:student_id>/',views.teacher_student_report,name='teacher_student_report'),

    path('teacher-dashboard/',views.teacher_dashboard,name='teacher_dashboard' ),
    path('teacher/attendance/view/',views.teacher_view_attendance,name='teacher_view_attendance'),

    

  
#Student dashboard===============================================================================
    path('student/marks/', views.student_marks, name='student_marks'),
    path('student/report/', views.student_report, name='student_report'),
    path('student/behaviour/',views.student_behavior,name='student_behavior'),
    path('student/attendance/',views.student_attendance,name='student_attendance'),
    path('student-dashboard/',views.student_dashboard, name='student_dashboard'),
    

#admin dashboard=================================================================================
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('system/add-students/',views.add_students,name='add_students'),
    path('system/students/',views.manage_students, name='manage_students'),
    path('system/edit-student/<int:student_id>/',views.edit_student,name='edit_student'),
    path('system/delete-student/<int:student_id>/',views.delete_student,name='delete_student'),


    path('system/add-teacher/',views.add_teacher, name='add_teacher'),
    path('system/edit-teacher/<int:teacher_id>/',views.edit_teacher,name='edit_teacher'),
    path('system/delete-teacher/<int:teacher_id>/',views.delete_teacher,name='delete_teacher'),
    path('system/teachers/',views.manage_teachers,name='manage_teachers'),
    path('system/add-notice/', views.add_notice, name='add_notice'),
    path('notices/', views.notices, name='notices'),


# API URLs========================================================================================
    path('api/students/', api_views.api_students, name='api_students'),
    path('api/attendance/<int:student_id>/',api_views.api_attendance,name='api_attendance'),
    path('api/marks/<int:student_id>/',api_views.api_marks,name='api_marks'),
    path('api/behavior/<int:student_id>/',api_views.api_behavior,name='api_behavior'),
    path('api/predict-behavior/',api_views.api_predict_behavior,name='api_predict_behavior'),
]