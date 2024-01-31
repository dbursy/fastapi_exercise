from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Annotated, Optional
import secrets
import pandas as pd
import os

# ----- Initiate FastAPI instance -----

description = """
The Datascience Quiz API helps you create questionnaires via a smartphone or web browser application 🚀

## Functionality
* Public endpoint to verify that the API is functional
* Private endpoints protected using Basic:Authentication
* Users can choose a test type (use) as well as one or more categories (subject)
* Can query MCQs of 5, 10 or 20 questions in a random order
* Can verify their their solution
* Amin user can create new questions

## Database 
* question: the title of the question
* subject : the category of the question
* correct : the list of correct answers
* use: the type of MCQ for which this question is used
* answerA : answer A
* answerB : answer B
* answerC : answer C
* answerD : the answer D (if it exists)
"""

api = FastAPI(
    title="Datascience Quiz API",
    description=description,
    version="1.0.0",
    contact={
        "name": "Dominik Bursy",
        "email": "dominik.bursy@icloud.com",
    },
    openapi_tags=[
    {
        'name': 'Public Endpoint',
        'description': 'Public endpoints that do not require any authentification'
    },
    {
        'name': 'User Endpoint',
        'description': 'Private endpoint accessible to users and admin users'
    },
    {
        'name': 'Admin Endpoint',
        'description': 'Private endpoint only accessible to admin users'
    }]
)

# ----- Authentification -----

# Add a basic HTTP authentication
security = HTTPBasic()

# Add user database
user_db = {
    "admin": "4dm1N",
    "alice": "wonderland",
    "bob": "builder",
    "clementine": "mandarine"
}

# Add user database
admin_db = {
    "admin": "4dm1N",
}

# Note: The admin has read and write access

def validate_user_credentials(user_credentials: HTTPBasicCredentials = Depends(security)):
    """
    Function to validate the user credentials
    """
    # Sotre user credentials
    # Optionally encode using .encode("utf-8")
    input_user_name = user_credentials.username
    input_user_password = user_credentials.password
    
    # Check if user exists in the user database
    if input_user_name in user_db:
        stored_user_name = input_user_name
        # Access the password from the user database
        stored_user_password = user_db[input_user_name]
    else:
        stored_user_name = str()
        stored_user_password = str()
    
    # Compare user credentials
    correct_user_name = secrets.compare_digest(input_user_name, stored_user_name)
    correct_user_password = secrets.compare_digest(input_user_password, stored_user_password)
    
    # Raise an authorization if the credentials mismatch
    if not (correct_user_name and correct_user_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    # Optionally return the username
    return user_credentials.username


def validate_admin_credentials(admin_credentials: HTTPBasicCredentials = Depends(security)):
    """
    Function to validate the admin credentials
    """
    # Sotre user credentials
    # Optionally encode using .encode("utf-8")
    input_admin_name = admin_credentials.username
    input_admin_password = admin_credentials.password
    
    # Check if user exists in the user database
    if input_admin_name in admin_db:
        stored_admin_name = input_admin_name
        # Access the password from the user database
        stored_admin_password = admin_db[input_admin_name]
    else:
        stored_admin_name = str()
        stored_admin_password = str()
    
    # Compare user credentials
    correct_admin_name = secrets.compare_digest(input_admin_name, stored_admin_name)
    correct_admin_password = secrets.compare_digest(input_admin_password, stored_admin_password)
    
    # Raise an authorization if the credentials mismatch
    if not (correct_admin_name and correct_admin_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    # Optionally return the admin name
    return admin_credentials.username

# ----- Initiate database -----

# df_questions = pd.read_excel('/Users/dominik.bursy/Documents/1_MLops/FastAPI/questions_en.xlsx')
df_questions = pd.read_excel(
    os.path.join(os.path.dirname("__file__"), 'data', 'questions_en.xlsx')
)

# ----- Public Endpoint -----

@api.get('/', name="Public Endpoint", tags=['Public Endpoint'])
def get_index():
    """
    Public endpoint that does not require any authentication
    """
    return "Welcome to the Datascience Quiz API"

# ----- User Endpoints: Query Questions -----

@api.get("/user", name="User Login", tags=['User Endpoint'])
def read_current_user(username: Annotated[str, Depends(validate_user_credentials)]):
    """
    - Private endpoing to verify user credentials
    - Returns the user name on successful connection
    """
    return {"username": username}

@api.get("/user/{use}/{subject}/{mcqs}", name="Query Questionnaire", tags=['User Endpoint'])
def return_questions(
    use: str, subject: str, mcqs: int,
    username: Annotated[str, Depends(validate_user_credentials)]
    ):
    """
    - Private endpoint that returns a questionnaire of 5,10, or 15 MCQs
    - Depends on the test type (use) and the categories (subject)
    """
    if mcqs in [5,10,15]:
        condition = (df_questions['use'] == use) & \
            (df_questions['subject'].str.contains(subject).any())
            #(df_questions['subject'].isin([subject]))
        df_filter = df_questions.loc[condition]
        try:
            df_filter_random = df_filter.sample(mcqs, random_state=1) # replace=True
            response_entries = ['question', 'responseA', 'responseB', 'responseC', 'responseD']
            return df_filter_random[response_entries].to_json()
        except:
            raise HTTPException(
            status_code=404,
            detail="Not enough questions available",
        )
    else: 
        raise HTTPException(
            status_code=404,
            detail="Please select MCQs of 5,10, or 15",
        )
    

# ----- Admin Endpoints: Post Questions -----

@api.get("/admin", name="Admin Login", tags=['Admin Endpoint'])
def read_current_user(username: Annotated[str, Depends(validate_admin_credentials)]):
    """
    - Private endpoing to verify admin user credentials
    - Returns the admin user name on successful connection
    """
    return {"username": username}

# ----- Amin User: Post Questions -----

class Question(BaseModel):
    """
    Question that is available in the questionnaire
    """
    question: str
    subject: str
    use: str
    correct: str
    responseA: str
    responseB: str
    responseC: Optional[str]
    responseD: Optional[str]
    remark: Optional[str] = None

@api.post('/admin/post_quesiton', name="Add Question", tags=['Admin Endpoint'])
def post_question(new_question: Question,
                  username: Annotated[str, Depends(validate_admin_credentials)]):
    """
    Create a new question within the database
    """
    global df_questions
    new_question = pd.DataFrame(new_question).T
    new_question.columns = new_question.iloc[0]
    new_question = new_question[1:]
    dfs = [df_questions, pd.DataFrame(new_question)]
    df_questions = pd.concat(dfs, ignore_index=True)
    #return new_question
    return df_questions.tail(1).to_json()
    

# ----- User: Get Solution -----

@api.get('/answer/{question_input}/{correct_input}', name="Verify Answer", tags=['User Endpoint'])
def get_item(question_input, correct_input,
             username: Annotated[str, Depends(validate_user_credentials)]
             ):
    """
    Verify the solution to a question
    """
    condition = (df_questions['question'] == question_input)
    if condition.sum() == 1:
        if df_questions.loc[condition, 'correct'].isna().values:
            return "No answer available"
        else:
            input_verification = correct_input.capitalize() in df_questions.loc[condition, 'correct'].values
            return {"Answer verification": str(input_verification).strip('[ ]')}
    else:
        return "Question is not available"