import dash_bootstrap_components as dbc
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from django.http import HttpRequest
from django_plotly_dash import DjangoDash  
import dash_daq as daq
from django.contrib.auth.models import User
from .models import Question, Choice, UserQuestionValue
import random

theme = dbc.themes.BOOTSTRAP

# Initialize the Dash app with Bootstrap
app = DjangoDash('MyDashApp', add_bootstrap_links=True, external_stylesheets=[theme, dbc.icons.BOOTSTRAP]) 

total_questions = 0
correct_answers = 0
incorrect_answers = 0
input_threshold = 10

# Load the quiz data from the database instead of a JSON file
questions = Question.objects.all()

def serve_layout():  
    return dbc.Container(
        [
            dbc.Row(dbc.Col(html.H1("Quiz_GCP - Digital Leader", className='text-center mb-4'), width=12)),
            html.Div(id='question-index', style={'display': 'none'}),
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
     Output('question-index', 'children')],
    [Input('next', 'n_clicks')],
    [State('answer', 'children'),
     State('input_threshold', 'value')],
    prevent_initial_call=True
)
def update_question(n_clicks,answer,threshold):
    if n_clicks >= 0 :
        global question_index, total_questions
        question_index1 = random.randint(0, len(questions) - 1)
        question_index2 = random.randint(0, len(questions) - 1) 
        while UserQuestionValue.objects.get(user=request.user, choice__question=questions[question_index1]).value < threshold or UserQuestionValue.objects.get(user=request.user, choice__question=questions[question_index2]).value < threshold:
            question_index1 = random.randint(0, len(questions) - 1)
            question_index2 = random.randint(0, len(questions) - 1)

        if UserQuestionValue.objects.get(user=request.user, choice__question=questions[question_index1]).value >= UserQuestionValue.objects.get(user=request.user, choice__question=questions[question_index2]).value:
            question_index = question_index1
        else:
            question_index = question_index2
        question = questions[question_index].question_text
        option_values = [choice.choice_text for choice in questions[question_index].choice_set.all()]
        options = [{'label': val, 'value': i+1} for i, val in enumerate(option_values)]
        if answer == "":
            total_questions += 0  
        else:
            total_questions += 1  
        return question, options, [], question_index
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

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
        global correct_answers, incorrect_answers
        correct_answer = [choice.id for choice in questions[question_index].choice_set.filter(is_correct=True)]
        user_choices = UserQuestionValue.objects.filter(user=request.user, choice__question=questions[question_index])
        if isinstance(correct_answer, list):
            if set(values) == set(correct_answer):
                correct_answers += 1
                for user_choice in user_choices:
                    user_choice.value -= 1
                    user_choice.save()
                return dbc.Alert([html.I(className="bi bi-check-circle-fill me-2"),"Correcto!",], color="success", style={"overflow": "auto","whiteSpace": "pre-wrap","font-size": "15px", "margig_top": '10px'}),
            else:
                incorrect_answers += 1
                for user_choice in user_choices:
                    user_choice.value += 1
                    user_choice.save()
                return dbc.Alert([html.I(className="bi bi-exclamation-circle-fill me-2"),"Incorrecto. La respuesta correcta es: {}.".format(correct_answer)], color="danger", style={"overflow": "auto","whiteSpace": "pre-wrap","fontSize": "larger","font-family": "Calibri"})
        else:
            if values[0] == correct_answer:
                correct_answers += 1
                for user_choice in user_choices:
                    user_choice.value -= 1
                    user_choice.save()
                return dbc.Alert([html.I(className="bi bi-check-circle-fill me-2"),"Correcto!",], color="success", style={"overflow": "auto","whiteSpace": "pre-wrap","font-size": "15px", "margig_top": '10px'}),
            else:
                incorrect_answers += 1
                for user_choice in user_choices:
                    user_choice.value += 1
                    user_choice.save()
                return dbc.Alert([html.I(className="bi bi-exclamation-circle-fill me-2"),"Incorrecto. La respuesta correcta es: {}.".format(correct_answer)], color="danger", style={"overflow": "auto","whiteSpace": "pre-wrap","fontSize": "larger","font-family": "Calibri"})
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
    Output('gauge-value', 'value'),
    [Input('next', 'n_clicks')])
def update_gauge(n_clicks):
    if n_clicks > 0:
        return UserQuestionValue.objects.get(user=request.user, choice__question=questions[question_index]).value

@app.callback(
    [Output("confirm", "displayed"), Output("confirm", "message")],
    [Input("open-explanation", "n_clicks")],
    [State("confirm", "displayed"), State("question-index", "children")]
)
def toggle_modal_and_update_message(n_clicks, is_open, question_index):
    if n_clicks is not None and n_clicks > 0:
        # Asegúrate de que question_index sea un número válido y esté dentro de los límites
        question_index = int(question_index)
        if 0 <= question_index < len(questions):
            return not is_open, questions[question_index].explanation
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
        user_choices = UserQuestionValue.objects.filter(user=request.user)
        for user_choice in user_choices:
            user_choice.value = 10
            user_choice.save()
        return "Los valores han sido restablecidos a 10."
    return ""

