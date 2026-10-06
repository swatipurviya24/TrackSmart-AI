from django.db import models
from django.contrib.auth.models import User

# Extend User model for different roles
class Profile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
        
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES,default='student')

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20)
    department = models.CharField(max_length=100)
    fee_status = models.CharField(max_length=10, choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], default='Unpaid')
    full_name = models.CharField(max_length=100,blank=True,null=True)
    mother_name = models.CharField(max_length=100,blank=True,null=True)
    father_name = models.CharField(max_length=100,blank=True,null=True)
    dob = models.DateField(blank=True,null=True)
    
    

    
    def __str__(self):
        return self.user.get_full_name()

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=[
            ('Present', 'Present'),
            ('Absent', 'Absent')
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'date'],
                name='unique_student_attendance_date'
            )
        ]

    def __str__(self):
        return f"{self.student.full_name} - {self.date} - {self.status}"

    
class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    marks = models.FloatField()



class BehaviorLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    activity = models.CharField(
        max_length=50,
        choices=[
            ('Attentive', 'Attentive'),
            ('Irrelevant', 'Irrelevant'),
            ('Sleeping', 'Sleeping'),
            ('Using_Mobile', 'Using_Mobile'),
        ]
    )

    def __str__(self):
        return f"{self.student.user.username} - {self.activity} @ {self.timestamp}"
    





class Teacher(models.Model):

    user = models.OneToOneField(User,on_delete=models.CASCADE)

    teacher_id = models.CharField(max_length=20,unique=True)

    name = models.CharField(max_length=100)

    subject = models.CharField(max_length=100)
    
    class_assigned = models.CharField(max_length=50)
    
    salary = models.IntegerField()

    def __str__(self):
        return self.name



class Notice(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)

    audience = models.CharField(
        max_length=20,
        choices=[
            ('All', 'All'),
            ('Students', 'Students'),
            ('Teachers', 'Teachers'),
        ]
    )

    def __str__(self):
        return self.title