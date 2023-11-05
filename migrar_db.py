import os
import json

# Configura Django para usar los modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_LoginQuiz_GCP.settings')

import django
django.setup()

from django.contrib.auth.models import User
from home.models import Question, Choice, UserQuestionValue

# Abre y lee el archivo JSON
with open('quiz.json', 'r') as f:
    data = json.load(f)

# Supongamos que ya tienes un usuario creado
# Intenta obtener el usuario
try:
    user = User.objects.get(username='jcampillay')
except User.DoesNotExist:
    # Si el usuario no existe, créalo
    user = User.objects.create_user(username='jcampillay', password='Jcampill8!')

# Itera sobre los datos y crea y guarda las instancias de tus modelos en la base de datos
for i in range(len(data['ques'])):
    question = Question(question_text=data['ques'][i], explanation=data['explanation'][i])
    question.save()

    for j in range(len(data['options'][i])):
        # Asegúrate de que data['ans'][i] sea una lista
        answers = data['ans'][i] if isinstance(data['ans'][i], list) else [data['ans'][i]]
        # Ahora puedes buscar en answers sin problemas
        is_correct = j+1 in answers

        choice = Choice(question=question, choice_text=data['options'][i][j], is_correct=is_correct)
        choice.save()

    user_question_value = UserQuestionValue(user=user, question=question, value=data['valores'][i])
    user_question_value.save()
