import dash_bootstrap_components as dbc
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from django.http import HttpRequest
from django_plotly_dash import DjangoDash  
import dash_daq as daq
from django.contrib.auth.models import User
from .models import Question, Choice, UserQuestionValue
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F  
import random

theme = dbc.themes.BOOTSTRAP

# Initialize the Dash app with Bootstrap
app = DjangoDash('MyDashApp', add_bootstrap_links=True, external_stylesheets=[theme, dbc.icons.BOOTSTRAP]) 

# Asume que ya tienes un usuario
user = User.objects.get(username='jcampillay')


user_id = user.id

total_questions = 0
correct_answers = 0
incorrect_answers = 0
input_threshold = 10

questions = Question.objects.all()

def serve_layout():  
    return dbc.Container(
        [
            dbc.Row(dbc.Col(html.H1("Quiz_GCP - Digital Leader", className='text-center mb-4'), width=12)),
            html.Div(id='question-index', style={'display': True}),
            dbc.Row(
                [
                    dbc.Col(html.H4(id='question', className='text-center mb-4'), width=12),
                    dbc.Col(
                                [
                                    dcc.Checklist(id='options', inputStyle={"margin-right": "20px"}),
                                ],
                                width={'size': 12, 'offset': 1},  
                            ),
                ],
                className='justify-content-center mb-4',
            ),
            dbc.Row(
                [
    dbc.Col(
        [
            html.Button('Submit', id='submit', n_clicks=0, style={'background-color': 'blue', 'color': 'white'}, className='mx-2'),
            html.Button('Next', id='next', n_clicks=0, style={'background-color': 'green', 'color': 'white'}, className='mx-2'),
            html.Span("Filtro", className="mx-2"),  
            dcc.Input(id='input_threshold', type='number', value=input_threshold, style={"width": "50px"}),  
            html.Button("Explanation", id="open-explanation", style={'background-color': 'yellow', 'color': 'black'}, className='mx-2'),
            html.Button("Reset Values", id="reset-values", style={'background-color': 'red', 'color': 'white'}, className='mx-2'), 
        ],
        width={'size': 6, 'offset': 1}, 
    ),
    dcc.ConfirmDialog(
        id="confirm",
        message="",
    ),
    dcc.ConfirmDialog(  
    id="confirm-reset",
    message="¿Seguro que desea resetar los valores?",
    ),
                ],
                className='justify-content-center',
            ),
            dbc.Col(html.Div(id='answer', className='text-center mt-4'), width={'size': 6, 'offset': 3}),
    dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Row(html.Div(id='total_questions', className='text-center'), className='mt-2 mb-1'),
                    dbc.Row(html.Div(id='correct_answers', className='text-center'), className='mt-2 mb-1'),
                    dbc.Row(html.Div(id='incorrect_answers', className='text-center'), className='mt-2 mb-1'),
                ],
                width=4,
                align="start"  
            ),
                dbc.Col(
                    daq.Gauge(
                        id='gauge-value',
                        size=150,
                        showCurrentValue=True,
                        color={"gradient":True,"ranges":{"green":[0,8],"yellow":[8,14],"red":[14,20]}},
                        value=0,
                        label='    ',
                        max=20,
                        min=0,
                    ),
                    width=4,
                )
        ],
        justify="center",
        align="center",  
    ),
    dcc.Store(id='next_clicked', data=0),
        ],
        fluid=True,
    )

app.layout = serve_layout  # Pasa la función serve_layout a app.layout.

@app.callback(
    [Output('question', 'children'),
     Output('options', 'options'),
     Output('options', 'value'),
     Output('question-index', 'children'),
     Output('gauge-value', 'value')],
    [Input('next', 'n_clicks')],
    [State('answer', 'children'),
     State('input_threshold', 'value'),
     State("question-index", "children")],
    prevent_initial_call=True
)
def update_question_and_gauge(n_clicks, answer, threshold, question_id):
    if n_clicks >= 0 :
        global question_index, total_questions, user_id

        user = User.objects.get(id=user_id)

        try:
            user_question_values = UserQuestionValue.objects.filter(user=user).order_by('?')[:2]

            while user_question_values[0].value < threshold or user_question_values[1].value < threshold:
                user_question_values = UserQuestionValue.objects.filter(user=user).order_by('?')[:2]

            if user_question_values[0].value >= user_question_values[1].value:
                selected_question = user_question_values[0].question
            else:
                selected_question = user_question_values[1].question

            question = selected_question.question_text
            option_values = [Choice.choice_text for Choice in selected_question.choice_set.all()]
            options = [{'label': val, 'value': i+1} for i, val in enumerate(option_values)]
            question_index = selected_question.id

            gauge_value = UserQuestionValue.objects.get(user=user, question=selected_question).value
        except ObjectDoesNotExist:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

        if answer == "":
            total_questions += 0  
        else:
            total_questions += 1  

        return question, options, [], question_index, gauge_value

    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output('answer', 'children'),
    [Input('submit', 'n_clicks'),
     Input('next_clicked', 'data')],
    [State('options', 'value')],
    prevent_initial_call=True)
def check_answer(submit_n_clicks, next_clicked, values):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'submit' and values is not None:
        global correct_answers, incorrect_answers, user_id

        user = User.objects.get(id=user_id)
        selected_question = Question.objects.get(id=question_index)

        correct_choices = list(selected_question.choice_set.order_by('id'))
        correct_answer_ids = [i+1 for i, choice in enumerate(correct_choices) if choice.is_correct]
        print('Respuesta correcta = ',correct_answer_ids)
        user_choice_ids = [choice.id for choice in Choice.objects.filter(id__in=values)]
        print('Resueta seleccionada = ',user_choice_ids)

        if set(user_choice_ids) == set(correct_answer_ids):
            correct_answers += 1
            UserQuestionValue.objects.filter(user=user, question=selected_question).update(value=F('value') - 1)
            return dbc.Alert([html.I(className="bi bi-check-circle-fill me-2"),"Correcto!",], color="success", style={"overflow": "auto","whiteSpace": "pre-wrap","font-size": "15px", "margig_top": '10px'}),
        else:
            incorrect_answers += 1
            UserQuestionValue.objects.filter(user=user, question=selected_question).update(value=F('value') + 1)
            return dbc.Alert([html.I(className="bi bi-exclamation-circle-fill me-2"),"Incorrecto. La respuesta correcta es: {}.".format(correct_answer_ids)], color="danger", style={"overflow": "auto","whiteSpace": "pre-wrap","fontSize": "larger","font-family": "Calibri"})
    elif button_id == 'next_clicked':
        return ""
    return dash.no_update

# Agrega estas funciones de devolución de llamada para actualizar los contadores en la interfaz de usuario
@app.callback(
    Output('total_questions', 'children'),
    [Input('next', 'n_clicks')])
def update_total_questions(n_clicks):
    return "Total de preguntas: {}".format(total_questions)

@app.callback(
    Output('correct_answers', 'children'),
    [Input('submit', 'n_clicks')],
    [State('options', 'value')])
def update_correct_answers(n_clicks, value):
    return "Respuestas correctas: {}".format(correct_answers)

@app.callback(
    Output('incorrect_answers', 'children'),
    [Input('submit', 'n_clicks')],
    [State('options', 'value')])
def update_incorrect_answers(n_clicks, value):
    return "Respuestas incorrectas: {}".format(incorrect_answers)

@app.callback(
    [Output("confirm", "displayed"), Output("confirm", "message")],
    [Input("open-explanation", "n_clicks")],
    [State("confirm", "displayed"), State("question-index", "children")]
)
def toggle_modal_and_update_message(n_clicks, is_open, question_id):
    if n_clicks is not None and n_clicks > 0:
        question_id = int(question_id)
        try:
            selected_question = Question.objects.get(id=question_id)
            return not is_open, selected_question.explanation
        except Question.DoesNotExist:
            pass
    return is_open, ""


@app.callback(
    Output('next_clicked', 'data'),
    [Input('next', 'n_clicks')],
    prevent_initial_call=True
)
def update_next_clicked(n_clicks):
    return n_clicks

@app.callback(
    Output("confirm-reset", "displayed"),
    [Input("reset-values", "n_clicks")]
)
def open_reset_dialog(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        return True
    return False

@app.callback(
    Output("confirm-reset", "message"),
    [Input("confirm-reset", "submit_n_clicks")]
)
def reset_values(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        # Asume que tienes el user_id disponible
        global user_id
        user = User.objects.get(id=user_id)
        
        # Ahora puedes usar 'user' en lugar de 'request.user'
        user_choices = UserQuestionValue.objects.filter(user=user)
        for user_choice in user_choices:
            user_choice.value = 10
            user_choice.save()
        return "Los valores han sido restablecidos a 10."

