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
                return 'Correcto'
            else:
                incorrect_answers += 1
                for user_choice in user_choices:
                    user_choice.value += 1
                    user_choice.save()
                return 'Incorrecto'
        else:
            if values[0] == correct_answer:
                correct_answers += 1
                for user_choice in user_choices:
                    user_choice.value -= 1
                    user_choice.save()
                return 'Correcto'
            else:
                incorrect_answers += 1
                for user_choice in user_choices:
                    user_choice.value += 1
                    user_choice.save()
                return 'Incorrecto'
    elif button_id == 'next_clicked':
        return ""
    return dash.no_update





####################


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
def update_question(n_clicks, answer, threshold):
    if n_clicks >= 0 :
        global question_index, total_questions, user_id

        user = User.objects.get(id=user_id)
        print('Usuario =',user)

        try:
            # Obtén un UserQuestionValue aleatorio para el usuario
            print('User Question =', UserQuestionValue.objects.filter(user=user).order_by('?').first())
            user_question_value = UserQuestionValue.objects.filter(user=user).order_by('?').first()
            print('user question 2 =',user_question_value.question.question_text)
            question = user_question_value.question.question_text
            option_values = [Choice.choice_text for Choice in user_question_value.question.choice_set.all()]
            print('Opciones Respuesta =',option_values)
            options = [{'label': val, 'value': i+1} for i, val in enumerate(option_values)]
            print('opciones resuesta 2 =', options)
            question_index = questions.index(user_question_value.question)
        except ObjectDoesNotExist:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update

        if answer == "":
            total_questions += 0  
        else:
            total_questions += 1  

        return question, options, [], question_index

    return dash.no_update, dash.no_update, dash.no_update, dash.no_update