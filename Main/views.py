from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from Main.models import *
from .forms import *
from django.contrib.auth import login,authenticate,logout as dj_logout
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormMixin
from django.http import HttpResponse, HttpResponseNotAllowed
import pandas  as pd
import plotly.express as px
import datetime


User = get_user_model()
#
context = {
}



#TODO DEVIN:
# Create superusers  & create a bunch of model objects through a super user and use it for dataframes
# Push it to PostgresSQL DB on Render so website authentication works and test further on website any potential bugs
"""
"id" is a the PK (actually called "id" ) of the Member field
"""

class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = CustomLoginForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, context={'form': form})
        
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
            else:
                messages.error(request, "Invalid credentials")
        return render(request, self.template_name, context={'form': form})


class WorkoutSessionListSearch(ListView):
    template_name = "search.html"
    model= WorkoutSession

    def get_queryset(self):
        """Return results by all fields 
        iexact = case insensitive
        Might be able to use slug-slug matches any ASCII characters & i think any field"""
        keyword = self.request.GET.get('keyword') #keyword is value in the URL definition in urls.py <str:keyword>
        if keyword is not None:
            try:
                matching_date = list(WorkoutSession.objects.filter(date__iexact=keyword)) 
                matching_duration = list(WorkoutSession.objects.filter(duration__iexact=keyword))
                matching_title = list(WorkoutSession.objects.filter(title__iexact=keyword))

                date_condition = Q(date__iexact=keyword)
                duration_condition = Q(duration__iexact=keyword)
                title_condition = Q(title__iexact=keyword)
                #TODO Toggle EXACT search with combined_condition = & with all these . | means "OR"
                combined_condition =  date_condition | duration_condition | title_condition

                matching_WorkoutSessions = WorkoutSession.objects.filter(combined_condition) 
                return matching_WorkoutSessions
            except Exception as e:   
                messages.warning(self.request,f'{e}')
                pass

        else: 
            return WorkoutSession.objects.all()
    
    def get_context_data(self, *args,**kwargs):
        context = super().get_context_data(**kwargs)
        context['keyword'] = self.request.GET.get('keyword','None')
        return context
    
@login_required
def log_weight(request):
    if request.method == 'POST':
        form = WeightHeightEntryForm(request.POST)
        if form.is_valid():
            weight_entry = form.save(commit=False)
            weight_entry.user = request.user
            weight_entry.save()
            return redirect('weight_history')
    else:
        form = WeightHeightEntryForm()
    
    return render(request, 'bmi.html', {'form': form})

def home(request):
    #TODO or Work Around the Homepage rendering everything - maybe can use global context dictionary and selectively add KV pairs
    """ EVERYTHING IS RENDER FROM THIS LOGIC ON THE HOMEPAGE """
    #global context?
    context = {
        'title': "Welcome to Gymcel-Hell",
        'registration': RegistrationForm(request.POST),
        'bmi': None,
        'bmi_plot': None,
        'weight_plot': None,
        "goal_bmi": None,
        "H-W form":None
    }
    if request.user.is_authenticated:
        profile = get_object_or_404(Profile, user=request.user)
        height = profile.height
        weight = profile.weight
        curr_bmi = weight / height  # Converserion Should be handled in models.py (height / 100) ** 2

        context['title'] = f"{request.user}'s Gym"
        context['UserWorkoutSessions'] = WorkoutSession.objects.filter(profile_id=request.user.id)
        context['createWorkoutSession'] = WorkoutSessionForm()
        context['bmi'] = curr_bmi
        context['registration'] = None
        context["goal_bmi"] = profile.Goal_BMI
        context["formset"] = SetFormSet()
        context["H-W form"] = WeightHeightEntryForm(request.POST)
        #TODO Get object attributes to populate charts (Use get_queryset against Profile w/ request.user ID)
        bmi_data = {
            'weight': [50, 60, 70, 80, 90], 
            'height': [150, 160, 170, 180, 190]
        }
        df_bmi = pd.DataFrame(bmi_data)
        df_bmi['bmi'] = df_bmi['weight'] / (df_bmi['height'] / 100) ** 2
        fig_bmi = px.scatter(df_bmi, x='height', y='weight', size='bmi', title='BMI Scatter Plot', labels={'height': 'Height (m)', 'weight': 'Weight (kg)'})
        context['bmi_plot'] = fig_bmi.to_html(full_html=False)

        # Weight Chart
        weight_data = [50, 60, 70, 80, 90]
        fig_weight = px.scatter(x=weight_data, y=weight_data, title='Weight Scatter Plot', labels={'x': 'Workout?!', 'y': 'Weight'})
        context['weight_plot'] = fig_weight.to_html(full_html=False)

        #TODO Height-to-weight Chare
        

    return render(request, 'home.html', context)

def registration(request):
    title = ""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main:home')
        else:
            messages.error(request, 'Those credentials do not work') #TODO Make it not appear when password and user information is too similar
    else:
        form = RegistrationForm()
    return render(request, 'home.html', {'title': title, 'registration': form})

def logout(request):
    if request.method == 'POST' or request.method == 'GET':
        dj_logout(request)
        messages.success(request,"Logout Successful")
    else:
        return HttpResponseNotAllowed(['POST', 'GET'])

    
   
def create_WorkoutSession(request):
    #TODO Graphs do no show up after submit becuase   - maybe use global context dictionary?
    title = "Create Workout" 
    if request.method == 'POST':
        form = WorkoutSessionForm(request.POST)
        formset = SetFormSet(request.POST) 
        #TODO:Actually test if the SetForm works as intended
        if form.is_valid() and formset.is_valid():
            profile = get_object_or_404(Profile, user=request.user)
            workout_session = form.save(commit=False)
            workout_session.profile = profile
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            workout_session.curr_body_weight = profile.weight
            duration = datetime.datetime.combine(datetime.date.today(), end_time) - datetime.datetime.combine(datetime.date.today(), start_time) #Added 
            workout_session.duration = duration 
            workout_session.save()
            sets = formset.save(commit=False)
            for set in sets:
                set.workout_session = workout_session
                set.save()
            formset.save_m2m()
            return redirect('main:home')
    else:  
        form = WorkoutSessionForm()
        formset = SetFormSet()
    
    return render(request, 'home.html', {'createWorkoutSession': form, "formset": formset, "title": title})

def update_WorkoutSession(request,WorkoutSession_id):
    WorkoutSession = get_object_or_404(WorkoutSession, WorkoutSession_id=WorkoutSession_id )
    title = f"Updating:{WorkoutSession.title}"
    form = WorkoutSessionForm(request.POST, instance=WorkoutSession)
    if form.is_valid():
            form.save()
            return redirect('main:home')

    return render(request, 'update.html', {'updateWorkoutSession': form, 'title': title , 'WorkoutSession':WorkoutSession})

def delete_WorkoutSession(request, title , WorkoutSession_id):
    """On button,click delete the WorkoutSession associated with the button""" 
    WorkoutSession = get_object_or_404(WorkoutSession, WorkoutSession_id=WorkoutSession_id , title=title)
    WorkoutSession.delete()
    return redirect('main:home')
    
class WorkoutSessionDetail(DetailView):
    """Detail already has PK handling"""
    model = WorkoutSession
    template_name = "WorkoutSession_detail.html"
    slug_url_kwarg = "title"
    pk_url_kwarg = "id" #need to actually tell the DetailView that this is explicitly the PK

    def get_context_data(self, **kwargs):
        context = super(WorkoutSessionDetail, self).get_context_data(**kwargs)
        #context['object'] = WorkoutSession.objects.filter(WorkoutSession_id= self.kwargs.WorkoutSession_id, title = self.kwargs.title) 
        return context
    