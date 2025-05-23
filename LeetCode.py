import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import re

from bs4 import BeautifulSoup


def login_leetcode(username, password):
    login_url = "https://leetcode.com/accounts/login/"

    options = Options()
    options.headless = False
    driver = webdriver.Chrome(service=Service('C:/Users/parham/PycharmProjects/LLM_Code_Debugging/chromedriver-win64'
                                              '/chromedriver.exe'), options=options)

    driver.get(login_url)
    time.sleep(5)

    driver.find_element(By.ID, 'id_login').send_keys(username)
    driver.find_element(By.ID, 'id_password').send_keys(password)

    input("Please solve the reCAPTCHA and press Enter to continue...")

    # driver.find_element(By.ID, 'signin_btn').click()
    # time.sleep(5)

    page_source = driver.page_source
    if re.search(r'isSignedIn:\s*true', page_source):
        print("Login successful!")

        session = requests.Session()
        for cookie in driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])

        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)

        driver.quit()
        return session
    else:
        print("Login failed!")

        with open('page_source_failed.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)

        driver.quit()
        return None


def get_user_info(session):
    user_info_url = "https://leetcode.com/api/problems/all/"

    response = session.get(user_info_url)

    if response.status_code == 200:
        user_info = response.json()

        filtered_problems = []
        for problem in user_info['stat_status_pairs']:
            if not problem['stat']['question__hide'] and not problem['paid_only']:
                filtered_problems.append({
                    'question__title_slug': problem['stat']['question__title_slug'],
                    'difficulty': problem['difficulty']['level']
                })

        with open('filtered_problems.json', 'w', encoding='utf-8') as f:
            json.dump(filtered_problems, f, ensure_ascii=False, indent=4)

        print("Filtered problems saved to filtered_problems.json")
        return filtered_problems
    else:
        print("Failed to get user information")
        return None


def search_problem(session, search_query, csrftoken):
    graphql_url = "https://leetcode.com/graphql"
    query = {
        "query": """
        query questionData($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                title
                titleSlug
                content
                difficulty
                likes
                dislikes
                isPaidOnly
                topicTags {
                    name
                    slug
                }
                companyTags {
                    name
                    slug
                }
                codeSnippets {
                    lang
                    langSlug
                    code
                }
            }
        }
        """,
        "variables": {
            "titleSlug": search_query
        }
    }

    headers = {
        "Content-Type": "application/json",
        "x-csrftoken": csrftoken,
        "referer": "https://leetcode.com"
    }

    response = session.post(graphql_url, json=query, headers=headers)

    if response.status_code == 200:
        problem_data = response.json()
        if 'errors' not in problem_data:
            # print(f"Search results for '{search_query}':")
            # print(json.dumps(problem_data, indent=4))
            return problem_data
        else:
            print(f"No results found for '{search_query}'")
            return None
    else:
        print("Failed to search for problem")
        return None


def submit_solution(session, problem_slug, solution_code, language, csrftoken, problem_id):
    submit_url = f"https://leetcode.com/problems/{problem_slug}/submit/"

    headers = {
        'Referer': f"https://leetcode.com/problems/{problem_slug}/",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/json',
        "x-csrftoken": csrftoken
    }

    payload = {
        "question_id": problem_id,
        "lang": language,
        "typed_code": solution_code,
    }

    print("Submitting solution...")
    print(f"Payload: {payload}")

    response = session.post(submit_url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Submission successful!")
        submission_id = response.json()
        submission_id = submission_id['submission_id']
        return submission_id
    else:
        print("Submission failed!")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def get_question_id(session, problem_slug):
    question_url = f"https://leetcode.com/graphql"
    headers = {
        'Referer': f"https://leetcode.com/problems/{problem_slug}/",
        'Content-Type': 'application/json',
    }
    payload = {
        "operationName": "questionData",
        "variables": {"titleSlug": problem_slug},
        "query": "query questionData($titleSlug: String!) { question(titleSlug: $titleSlug) { questionId } }"
    }

    print("Fetching question ID...")
    print(f"Payload: {payload}")

    response = session.post(question_url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        question_id = data['data']['question']['questionId']
        print(f"Question ID: {question_id}")
        return question_id
    else:
        print("Failed to get question ID")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def get_all_submissions(session, csfrtoken):
    with open("all_submissions.json", "r") as in_file:
        data = json.load(in_file)

    submissions_url = f"https://leetcode.com/api/submissions/"
    offset = 60
    limit = 20

    flag = True

    while flag:
        response = session.get(submissions_url + "?offset=" + str(offset) + "&limit=" + str(limit),
                               headers={"x-csrftoken": csfrtoken})

        if response.status_code == 200:
            submission = response.json()

        else:
            print("Failed to get submissions")
            print(response.status_code)
            print(len(data))
            break

        if submission["has_next"]:
            offset += limit

        else:
            flag = False

        for submission in submission["submissions_dump"]:
            data.append(submission)

    with open('all_submissions1.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_submission_details(session, csrftoken, submission_id):
    graphql_url = "https://leetcode.com/graphql"
    query = {
        "query": """
            query submissionDetails($submissionId: Int!) {
                submissionDetails(submissionId: $submissionId) {
                    runtime
                    runtimeDisplay
                    runtimePercentile
                    runtimeDistribution
                    memory
                    memoryDisplay
                    memoryPercentile
                    memoryDistribution
                    code
                    timestamp
                    statusCode
                    user {
                        username
                        profile {
                            realName
                            userAvatar
                        }
                    }
                    lang {
                        name
                        verboseName
                    }
                    question {
                        questionId
                        titleSlug
                        hasFrontendPreview
                    }
                    notes
                    flagType
                    topicTags {
                        tagId
                        slug
                        name
                    }
                    runtimeError
                    compileError
                    lastTestcase
                    codeOutput
                    expectedOutput
                    totalCorrect
                    totalTestcases
                    fullCodeOutput
                    testDescriptions
                    testBodies
                    testInfo
                    stdOutput
                }
            }
        """,
        "variables": {
            "submissionId": submission_id
        }
    }

    headers = {
        "Content-Type": "application/json",
        "x-csrftoken": csrftoken,
        "referer": f"https://leetcode.com/",
    }

    response = session.post(graphql_url, json=query, headers=headers)

    if response.status_code == 200:
        submission_data = response.json()

        status = "Unknown Error"
        print(submission_data["data"]["submissionDetails"]["statusCode"])
        if submission_data["data"]["submissionDetails"]["statusCode"] == 10:
            status = "Accepted"
        elif submission_data["data"]["submissionDetails"]["statusCode"] == 11:
            status = ("The above code returns the wrong answer for the following test case: " + "\n Test case inputs: "
                      + submission_data["data"]["submissionDetails"]["lastTestcase"] + "\n Code output: "
                      + submission_data["data"]["submissionDetails"]["codeOutput"] + "\n Expected output: "
                      + submission_data["data"]["submissionDetails"]["expectedOutput"])
        elif submission_data["data"]["submissionDetails"]["statusCode"] == 14:
            status = ("The above code exceeds the time limit. Here is the test case when the time limit is exceeded: "
                      + "\n Test case inputs: " + submission_data["data"]["submissionDetails"]["lastTestcase"] + "\n Expected output: "
                      + submission_data["data"]["submissionDetails"]["expectedOutput"])
        elif submission_data["data"]["submissionDetails"]["statusCode"] == 15:
            status = ("The above code returns the following error: " + submission_data["data"]["submissionDetails"]["runtimeError"]
                      + "\n this error is classified as Runtime Error")
        elif submission_data["data"]["submissionDetails"]["statusCode"] == 20:
            status = ("The above code returns the following error: " + submission_data["data"]["submissionDetails"]["compileError"]
                      + "\n this error is classified as Compile Error")

        return status

    else:
        print(f"Failed to fetch submission details. Status code: {response.status_code}")


# if __name__ == "__main__":
#     username = "An0therD4y"
#     password = "YAe3qh:5MsGVp!d"
#
#     submission_id = 1362893504
#
#     session = login_leetcode(username, password)
#     csrftoken = session.cookies.get('csrftoken')
#
#     solution_code = """class Solution {
# public:
#     vector<int> twoSum(vector<int>& nums, int target) {
#         unordered_map<int, int> num_map;
#         for (int i = 0; i < nums.size(); i++) {
#             int complement = target - nums[i];
#             if (num_map.find(complement) != num_map.end()) {
#                 return {num_map[complement], i};
#             }
#             num_map[nums[i]] = i;
#         }
#         return {};
#     }
# };"""
#
#     problem_slug = "two-sum"
#     question = search_problem(session, problem_slug, csrftoken)
#     question_id = question['data']['question']['questionId']
#     print(submit_solution(session, problem_slug, solution_code, 'cpp', csrftoken, question_id))
#
#     # print(get_submission_details(session, csrftoken, submission_id))
