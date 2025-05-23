import time

import requests

import GPT
import LeetCode
import json
from bs4 import BeautifulSoup


def html_to_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()


if __name__ == '__main__':
    USERNAME = "YOUR_LEETCODE_USERNAME"
    PASSWORD = "YOUR_LEETCODE_PASSWORD"

    session = LeetCode.login_leetcode(USERNAME, PASSWORD)
    csrftoken = session.cookies.get('csrftoken')
    gpt = GPT.GPT()

    questions_file = open('questions_to_solve.json')
    questions = json.load(questions_file)

    questions = questions[39:]

    question_num = 39
    for curr_question in questions:

        time.sleep(10)
        question = LeetCode.search_problem(session, curr_question['question__title_slug'], csrftoken)
        question_id = question['data']['question']['questionId']
        question_content = question['data']['question']['content']
        code_snippet = question['data']['question']['codeSnippets'][0]['code']

        question_content = html_to_text(question_content)

        messages = [{'role': 'system', 'content': 'You are a skilled C++ code generator and debugger. Your task is to '
                                                  'generate code based on the given question and debug any issues in the '
                                                  'provided code using the feedback given.'},
                    {'role': 'user', 'content': "This is a LeetCode problem, Please provide the full C++ code solution, "
                                                "also divide the code into smaller easy to explain segments and explain them at the end of your response, "
                                                "note that a code segment can be as short as one line and can be as "
                                                "long as multiple lines. The provided"
                                                "code has to be in the following format: \n" + code_snippet + "\n The question is as "
                                                                                                              "follows: \n" +
                                                question_content}]
        for i in range(5):
            gpt4_response = gpt.communicate(messages)

            start = gpt4_response.find('```')
            code = gpt4_response[start + 3:]
            end = code.find('```')
            code = code[:end]
            code = code.replace('```', '')
            code = code.replace('cpp', '')

            time.sleep(10)
            response = LeetCode.submit_solution(session, curr_question['question__title_slug'], code, 'cpp',
                                                csrftoken, question_id)
            if response is None:
                while True:
                    time.sleep(10)
                    response = LeetCode.submit_solution(session, curr_question['question__title_slug'], code, 'cpp',
                                                        csrftoken, question_id)
                    if response is not None:
                        break

            time.sleep(10)
            unit_test = LeetCode.get_submission_details(session, csrftoken, response)
            messages.append({'role': 'system', 'content': gpt4_response})
            messages.append({'role': 'user', 'content': unit_test})

            print(f"Current iteration: {i+1}/5")
            print(messages)
            print("_____________________________________________________________________________________")

            if unit_test == "Accepted":
                break

        question_num += 1
        print("Current Question:" + str(question_num))
