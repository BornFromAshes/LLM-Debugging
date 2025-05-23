import json


def problem_cleaner():
    questions_file = open('filtered_problems.json')
    questions = json.load(questions_file)
    easy_problems = []
    for question in questions:
        if question['difficulty'] == 1:
            easy_problems.append(question)

    with open('easy_problems.json', 'w') as outfile:
        json.dump(easy_problems, outfile)


def problem_counter():
    questions_file = open('questions_to_solve.json')
    questions = json.load(questions_file)

    print(len(questions))


def questions_cleaner():
    questions_file = open('easy_problems.json')
    questions = json.load(questions_file)
    cleaned_questions = []
    with open('questions_to_remove.txt', 'r') as infile:
        questions_to_remove = infile.read().splitlines()

    for question in questions:
        if question['question__title_slug'] not in questions_to_remove:
            cleaned_questions.append(question)

    with open('cleaned_questions.json', 'w') as outfile:
        json.dump(cleaned_questions, outfile)


def duplicate_questions_cleaner():
    questions_file = open('all_submissions.json')
    questions = json.load(questions_file)

    duplicated_questions = []
    cleaned_questions = []

    for question in questions:
        if question['question_id'] not in duplicated_questions:
            cleaned_questions.append(question)
            duplicated_questions.append(question['question_id'])

    with open('all_submissions.json', 'w') as outfile:
        json.dump(cleaned_questions, outfile)


def statistics():
    questions_file = open('all_submissions.json')
    questions = json.load(questions_file)

    accepted = 0
    wrong_answer = 0
    compile_error = 0
    runtime_error = 0
    time_limit_exceeded = 0

    for question in questions:
        if question['status_display'] == "Accepted":
            accepted += 1
        elif question['status_display'] == "Wrong Answer":
            wrong_answer += 1
        elif question['status_display'] == "Compile Error":
            compile_error += 1
        elif question['status_display'] == "Runtime Error":
            runtime_error += 1
        elif question['status_display'] == "Time Limit Exceeded":
            time_limit_exceeded += 1

    print(accepted)
    print(wrong_answer)
    print(compile_error)
    print(runtime_error)
    print(time_limit_exceeded)


def questions_to_solve():
    all_submissions = open('all_submissions.json')
    submissions = json.load(all_submissions)

    questions = open('cleaned_questions.json')
    cleaned_questions = json.load(questions)

    accepted = []
    for submission in submissions:
        if submission['status_display'] == "Accepted":
            accepted.append(submission['title_slug'])

    not_accepted = []
    for question in cleaned_questions:
        if question['question__title_slug'] not in accepted:
            not_accepted.append(question)

    with open('questions_to_solve.json', 'w') as outfile:
        json.dump(not_accepted, outfile)


def confirmation():
    questions_file = open('questions_to_solve.json')
    questions = json.load(questions_file)

    submissions_file = open('all_submissions.json')
    submissions = json.load(submissions_file)
    title = []
    for question in questions:
        title.append(question['question__title_slug'])

    for submission in submissions:
        if submission['title_slug'] in title:
            print(submission['title_slug'] + ": " + submission['status_display'])
            print("_____________________________________________________________________________")


if __name__ == "__main__":
    confirmation()

