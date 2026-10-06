from django.test import TestCase
from .models import Attendance, BehaviorLog


class TrackSmartModelTests(TestCase):

    def test_attendance_has_unique_student_date_constraint(self):
        constraints = Attendance._meta.constraints

        self.assertTrue(
            any(
                constraint.name == 'unique_student_attendance_date'
                for constraint in constraints
            )
        )

    def test_behavior_log_has_correct_activity_choices(self):
        field = BehaviorLog._meta.get_field('activity')

        choices = [choice[0] for choice in field.choices]

        self.assertEqual(
            choices,
            [
                'Attentive',
                'Irrelevant',
                'Sleeping',
                'Using_Mobile'
            ]
        )