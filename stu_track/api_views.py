from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .ml.predictor import predict_behavior
import os
import uuid

from .models import Student, Attendance, Marks, BehaviorLog
from .serializers import (
    StudentSerializer,
    AttendanceSerializer,
    MarksSerializer,
    BehaviorLogSerializer
)


# Get all students
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_students(request):

    students = Student.objects.all()

    serializer = StudentSerializer(
        students,
        many=True
    )

    return Response(serializer.data)


# Get attendance of one student
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_attendance(request, student_id):

    attendance = Attendance.objects.filter(
        student_id=student_id
    )

    serializer = AttendanceSerializer(
        attendance,
        many=True
    )

    return Response(serializer.data)


# Get marks of one student
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_marks(request, student_id):

    marks = Marks.objects.filter(
        student_id=student_id
    )

    serializer = MarksSerializer(
        marks,
        many=True
    )

    return Response(serializer.data)


# Get behavior of one student
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_behavior(request, student_id):

    behaviors = BehaviorLog.objects.filter(
        student_id=student_id
    )

    serializer = BehaviorLogSerializer(
        behaviors,
        many=True
    )

    return Response(serializer.data)



# AI behavior prediction
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_predict_behavior(request):

    if 'image' not in request.FILES:
        return Response({
            'error': 'Please upload an image'
        })

    image_file = request.FILES['image']

    image_path = image_path = f'temp_ai_{uuid.uuid4().hex}.jpg'

    try:
        with open(image_path, 'wb+') as file:
            for chunk in image_file.chunks():
                file.write(chunk)

        prediction = predict_behavior(image_path)

        return Response({
            'prediction': prediction
        })

    finally:
        if os.path.exists(image_path):
            os.remove(image_path)





           