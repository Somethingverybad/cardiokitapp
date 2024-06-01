
import csv

import numpy as np
import plotly.graph_objs as go
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db.models import Max
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from .forms import LoginForm
from .forms import ManualDataForm
from .forms import RegistrationForm
from .models import PatientData
from .serializers import PatientDataSerializer


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('personal_cabinet')  # Перенаправление на личный кабинет после входа
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})



def logout_view(request):
    logout(request)
    return redirect('login')  # Перенаправление на страницу входа после выхода



@login_required
def personal_cabinet_view(request):
    # Логика для отображения информации в личном кабинете
    user = request.user
    user_groups = user.groups.all()
    group_names = list(user_groups)  # Преобразование QuerySet в список для удобства работы
    if len(group_names)!=0:
        group_name = group_names[0]  # Получение первого элемента списка (если он существует)
        # Теперь переменная group_name содержит только название группы в строковом формате
    else:
        group_name="Patient"
    doc = 'Doctors'
    print(group_name)
    context = {
        'user': user,
        'user_groups': user_groups,
        'group_name': str(group_name),
        'doc':doc,

    }
    return render(request, 'personal_cabinet.html', context)




def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Перенаправление на страницу входа после успешной регистрации
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def patients(request):

    group = Group.objects.get(name='Patient')
    patients_data = group.user_set.all()
    return render(request, 'patients.html', {'patients': patients_data})

def clear_patient_data(request, user_id):
    PatientData.objects.filter(user=user_id).delete()
    print("Данные пациента очищены \n")
    return HttpResponseRedirect('/social/patient/'+str(user_id)+'/')  # Перенаправление на страницу профиля после добавления данных


def clear_patient_data_last_day(request, user_id):
    # Находим последнюю внесенную дату для данного пользователя
    last_entry_date = PatientData.objects.filter(user=user_id).aggregate(last_date=Max('date'))['last_date']

    if last_entry_date is not None:
        # Удаление данных за последний день
        PatientData.objects.filter(user=user_id, date=last_entry_date).delete()
        print(f"Данные пациента за {last_entry_date} удалены \n")
    else:
        print("Нет данных для удаления \n")

    return HttpResponseRedirect('/social/patient/' + str(user_id) + '/')

def profile_pat(request, user_id):
    user = User.objects.get(id=user_id)
    print(request.session.get('csv_filename'))
    usergr = request.user
    user_groups = usergr.groups.all()
    group_names = list(user_groups)  # Преобразование QuerySet в список для удобства работы
    if len(group_names) != 0:
        group_name = group_names[0]  # Получение первого элемента списка (если он существует)
        # Теперь переменная group_name содержит только название группы в строковом формате
    else:
        group_name = "Patient"
    doc = 'Doctors'
    print(group_name)

    if request.method == 'POST':
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            if 'csv_filename' in request.session:
                del request.session['csv_filename']  # Удаляем старое имя файла из сессии
            request.session['csv_filename'] = csv_file.name

            decoded_file = csv_file.read().decode('utf-8').splitlines()
            csv_reader = csv.reader(decoded_file)

            for row in csv_reader:
                date = row[0]
                time = row[1]
                SpO2 = row[2]
                HBR = row[3]
                temper = row[4]
                PatientData.objects.create(user=user, date=date, time=time, spo2=SpO2, heart_rate=HBR,
                                           body_temperature=temper)

            return redirect('profile_pat', user_id=user_id)  # Перенаправляем на GET запрос после успешной обработки POST

    patient_data = PatientData.objects.filter(user=user)
    avgSpO2 = ['average SpO2', np.average(PatientData.objects.filter(user=user_id).values_list('spo2', flat=True))]
    avgHbr = ['average Heart Rate', round(np.average(PatientData.objects.filter(user=user_id).values_list('heart_rate', flat=True)), 0)]
    avgtemp = ['average Temperature', round(np.average(PatientData.objects.filter(user=user_id).values_list('body_temperature', flat=True)), 1)]

    if avgSpO2[1] < 95:
        statSpO2 = "Низкий уровень кислорода в крови"
    elif 95 <= avgSpO2[1] < 98:
        statSpO2 = "Уровень кислорода в крови нормальный"
    elif avgSpO2[1] >= 98:
        statSpO2 = "Кровь насыщена кислородом"
    else:
        statSpO2 = "Нет данных"

    if avgHbr[1] < 60:
        statHbr = "Медленный пульс"
    elif 60 <= avgHbr[1] < 90:
        statHbr = "Нормальный пульс"
    elif avgHbr[1] > 90:
        statHbr = "Высокий пульс"
    else:
        statHbr = "Нет данных"

    if avgtemp[1] < 35:
        stattemp = "Низкая температура"
    elif 35 <= avgtemp[1] < 38:
        stattemp = "Нормальная температура"
    elif avgtemp[1] >= 38:
        stattemp = "Средняя температура повышенная"
    else:
        stattemp = "Нет данных"


        # Создание списков для данных по осям X и Y
    dates_times = []
    spo2_values = []
    heart_rate_values = []
    body_temperature_values = []

    for data_point in patient_data:
        dates_times.append(str(data_point.date) + ' ' + str(data_point.time))
        spo2_values.append(data_point.spo2)
        heart_rate_values.append(data_point.heart_rate)
        body_temperature_values.append(data_point.body_temperature)

            # Создание линий графика
    spo2_trace = go.Scatter(x=dates_times, y=spo2_values, mode='lines', name='SpO2')
    heart_rate_trace = go.Scatter(x=dates_times, y=heart_rate_values, mode='lines', name='Heart Rate')
    body_temperature_trace = go.Scatter(x=dates_times, y=body_temperature_values, mode='lines',
                                                name='Body Temperature')

            # Создание макета графика
    layout = go.Layout(title='Patient Data', xaxis=dict(title='Date and Time'), yaxis=dict(title='Value'))

            # Создание объекта Figure и вставка трасс
    fig = go.Figure(data=[spo2_trace, heart_rate_trace, body_temperature_trace], layout=layout)

            # Конвертация объекта Figure в HTML-разметку
    plot_html = fig.to_html(full_html=False)



    context = {'user': user, 'patient_data': patient_data,
               'avgSpO2': round(avgSpO2[1],2), 'avgHbr': avgHbr[1], 'avgtemp': avgtemp[1],
               'statHBR': statHbr, 'stattemp': stattemp, 'statSpO2': statSpO2, 'user_id': user_id, 'doc':doc, 'user_groups': user_groups,
        'group_name': str(group_name),'plot_html': plot_html}

    return render(request, 'profile_pat.html', context)

def plot_patient_data(request, user_id):
    user = User.objects.get(id=user_id)
    # Получение данных пациента из базы данных
    patient_data = PatientData.objects.filter(user=user)

    # Создание списков для данных по осям X и Y
    dates_times = []
    spo2_values = []
    heart_rate_values = []
    body_temperature_values = []

    for data_point in patient_data:
        dates_times.append(str(data_point.date) + ' ' + str(data_point.time))
        spo2_values.append(data_point.spo2)
        heart_rate_values.append(data_point.heart_rate)
        body_temperature_values.append(data_point.body_temperature)

    # Формирование словаря с данными
    data = {
        'user_id': user_id,
        'dates_times': dates_times,
        'spo2_values': spo2_values,
        'heart_rate_values': heart_rate_values,
        'body_temperature_values': body_temperature_values
    }

    # Возврат JSON-ответа
    return JsonResponse(data)


def plot_page(request, user_id):
    plot_patient_data_url = reverse('plot_patient_data', kwargs={'user_id': user_id})
    return render(request, 'plot_page.html', {'user_id': user_id, 'plot_patient_data_url': plot_patient_data_url})

def some_other_view(request):
    if 'csv_filename' in request.session:
        csv_filename = request.session['csv_filename']
        print(csv_filename)
    else:
        csv_filename = None






class PatientDataList(generics.ListCreateAPIView):  # Изменили ListAPIView на ListCreateAPIView
    queryset = PatientData.objects.all()
    serializer_class = PatientDataSerializer

    def post(self, request, *args, **kwargs):
        serializer = PatientDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def add_manual_data(request,user_id):
    if request.method == 'POST':
        form = ManualDataForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            PatientData.objects.create(
                user=request.user,
                date=data['date'],
                time=data['time'],
                spo2=data['spo2'],
                heart_rate=data['heart_rate'],
                body_temperature=data['body_temperature']
            )

            r=user_id
            print(r)
            return HttpResponseRedirect('/social/patient/'+str(user_id)+'/')  # Перенаправление на страницу профиля после добавления данных
    else:
        form = ManualDataForm()

    return render(request, 'add_manual_data.html', {'form': form})

