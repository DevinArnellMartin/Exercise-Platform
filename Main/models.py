from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

"""
to_field attr => lets Django know which field to reference of the relationship default would be the primary key which is usually a number

"""
class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)
    BMI = models.FloatField(null=True, blank=True)  # Allow null and blank values initially

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    height = models.IntegerField()  #TODO Height in centimeters
    weight = models.IntegerField()  #TODO Weight in kilograms
    BMI = models.FloatField(null=True, blank=True)  

    def save(self, *args, **kwargs):
        if self.height and self.weight:
            height_in_meters = self.height / 100
            self.BMI = self.weight / (height_in_meters ** 2)
        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username

#TODO:Fix model redundancy 
class Exercise(models.Model):
    class ExerciseType(models.TextChoices):
        CARDIO = 'Cardio', _('Cardio')
        WEIGHT_LIFTING = 'Weight-Lifting', _('Weight-Lifting')
        CALISTHENICS = 'Calisthenics', _('Calisthenics')
        HIIT = 'HIIT', _('HIIT')
        CROSSFIT = 'Crossfit', _('Crossfit')

    name = models.CharField(max_length=100)
    exercises = models.ManyToOneRel("WorkoutSession","WorkoutSession",
                                    field_name="exercise",related_name="exercises")
    name = models.CharField(max_length=100)
    exercise_type = models.CharField(
        max_length=20,
        choices=ExerciseType.choices,
        default=ExerciseType.CARDIO,
    )

    def __str__(self):
        return self.name

class WorkoutSession(models.Model):
    class WorkoutType(models.TextChoices):
        CARDIO = 'Cardio', _('Cardio')
        WEIGHT_LIFTING = 'Weight-Lifting', _('Weight-Lifting')
        CALISTHENICS = 'Calisthenics', _('Calisthenics')
        HIIT = 'HIIT', _('HIIT')
        CROSSFIT = 'Crossfit', _('Crossfit')

    title = models.TextField(blank=True , null=False)
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    duration = models.TimeField()
    workout_type = models.CharField(
        max_length=20,
        choices=WorkoutType.choices,
        blank=True,
    )

    def __str__(self):
        return f"{self.profile.user.username} - {self.date}"
    
    def determine_workout_type(self):
        exercise_types = self.exercises.values_list('exercise_type', flat=True)
        if exercise_types:
            return max(set(exercise_types), key=exercise_types.count)
        return WorkoutSession.WorkoutType.CARDIO 

class Set(models.Model):
    workout_session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    reps = models.IntegerField()
    weight = models.FloatField()

    def __str__(self):
        return f"{self.workout_session.profile.user.username} - {self.exercise.name} - {self.reps} reps @ {self.weight} lbs"

