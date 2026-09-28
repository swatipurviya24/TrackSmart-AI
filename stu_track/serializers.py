from rest_framework import serializers
from .models import Student, Attendance, Marks, BehaviorLog


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = [
            'id',
            'full_name',
            'roll_number',
            'department',
            'fee_status',
            'mother_name',
            'father_name',
            'dob'
        ]


class AttendanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attendance
        fields = [
            'id',
            'student',
            'date',
            'status'
        ]


class MarksSerializer(serializers.ModelSerializer):

    class Meta:
        model = Marks
        fields = [
            'id',
            'student',
            'subject',
            'marks'
        ]


class BehaviorLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = BehaviorLog
        fields = [
            'id',
            'student',
            'timestamp',
            'activity'
        ]