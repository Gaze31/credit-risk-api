# it is frame work for credit risk
from fastapi import FastAPI
#CORS allows other module to call my api
from fastapi.middleware.cors import CORSMiddleware
#pydantic is used for data validation and if someone sends string and i expect number means this error it will handle that error and sends proper response
from pydantic import BaseModel
#pickel is used to save my ML model
import pickle
#numpy handles arrays and mathematical operations
import numpy as np

# Load model
#this opens the graident boosting model which is trained and saved in the model folder and rb means read binary and loads the model into the variable model
with open("model/credit_model.pkl", "rb") as f:
    model = pickle.load(f)

  # even this opens the scaler which is used to scale the grident boosting model  input data and features where it read binary and loads the features which are used in the model  
with open("model/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)
    #in this it opens the features where the graident boosting model marksup the required features and it used to calculate the feature importanceand also to make sure the input data is in the same order
with open("model/features.pkl", "rb") as f:
    features = pickle.load(f)

#it initializzes the Fast API 
app = FastAPI(
    #title is the name of API and description is the short description about the API
    title="Credit Risk API",
    description="ML-powered loan default prediction | AUC-ROC: 0.897",
    #Ffor versioning of API To keep track of changes and updates to the API
    version="1.0.0"
)

#CORS middleware is added to allow cross-origin requests from any domain, which is essential for frontend applications hosted on different domains.  
app.add_middleware(   
    CORSMiddleware,
#allow_origins=[*] means allow all origins to access the API, WHhich is useful during the developmet phase but should be rescrticted in productionfor security reasons.    
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
#Loanapplication is a Pydantic model that defines the excepted input data structure for the / predict endpoint. it includes fields like loan amount, interest rate, annual income, debt-to-income ratio, and other relevant financial and credict histroy features. each field has a default value which is used for testing an documentation purposes.
class LoanApplication(BaseModel):
    loan_amnt: float = 15000
    int_rate: float = 12.5
    annual_inc: float = 60000
#dti stands for debt- to income ratio which is a measure of a borrower's monthly debt payments comapred to their montly gross income. it is used by lenders to assess a borrower's ability to manage montly payments and is a key factor in credit risk assessment    
    dti: float = 18.5
#delinq_2yrs stands for delinquencies in the pastt 2 yrs which is a measure of how many times a borrower has been delinquent on their credit obligations in the past 2 years. a delinquency occurs when a borrower fails to make a payment on time, and it is an important factor in credit risk asssessment. lenders use this information to evaluation a borrower's creditwprthiness and  to determine the likelihood of future delinquencies. a higher number of delinquencies in the past 2 years generally indicates a higher credit risk.    
    delinq_2yrs: int = 0
#inq_last_6mths stands for inquiries in the last 6 months which is a measure of how many times a borrower has applied for credit in the past 6 months. each time a borrower applies for credit, it results in a hard inquiry on their credit report, which can temporarily lower their credit score. lenders use this information to assess a borrowers credit-seeking behavior and to evaluate their credit risk. a higher number of inquiries in the last 6 months may indicate that a borrower is actively seeking credit, which can be a red flag for lenders and may suggest a higher credit risk.    
    inq_last_6mths: int = 1
#open_acc stands for open accounts which is a measure of how many credit accounts a borrower currently has open. this includes credit cards, loans and other types of credit accounts. lenders use this information to assess a borrower's credit utilization and overall credit managemnent. a higher number of open accounts can indicate that a borrower is actively using credit, which may be a positive sign of credit management but can also indicate a higher credit risk if
    open_acc: int = 8
#revol_util stands for revolving utilization which is a measure of how much of a borrower's available revolving credit they are currently using. it is calculated by dividing the total revolving balance by the total recolving credit limit and multiplying by 100 to get a percentage. lenders use this information to assess a borrower's credit utilization and overall credit management. a higher revolving utilization can indicate that a borrower is relying heavily on their available credit, which may be a red flag for lenders and can suggest a higher credit risk. generally, it is recommended to keep revolving utilization below 30% to maintain a healthy credit profile.   
    revol_util: float = 45.0 
#total_acc stands for total accounts which is a measure of the total number of credit accounts a borrower has ever had, including both open and closed accounts. lenders use this information to assess a borrower's credit history and overall credit management. a higher number of total accounts can indicate that a borrower has a longer credit history and may have more experience managing credit, which can be a positive sign for lenders. however, it can also indicate a higher credit risk if the borrower has a history of mismanaging credit or has had many accounts closed due to delinquency.    
    total_acc: int = 15
#emp_length stands for employment length which is a measure of how long a borrower has been employed at their current job. it is typically measured in years and can be an important factor in credit risk assessment. lenders use this information to evaluate a borrower's stability and reliability as a borrower. generally, a longer employment length is seen as a positive sign for lenders, as it can indicate that the borrower has a stable source of income and may be more likely to repay their debts. however, it is important to consider other factors such as the borrower's overall financial situation and credit history when assessing credit risk.     
    emp_length: int = 3

#RiskResponse is a Pydantic model that defines the structure of the response returned by the /predict endpoint. it includes fields such as default probability, risk tier, risk score, recommendation and feature importance. this model helps to ensure that the API returns consistent and well-structured responses to clients, making it easier for them to understand and utilize the information provided by the credit risk scoring API.-ppp
class RiskResponse(BaseModel):
# default_probability is the predicted probability that a borrower will default on their loan, which is calculated by the machine learning model based on the input features provided in the loan application. this value is typically expressed as a decimal between 0 and 1, where a higher value indicates a higher likelihood of default. lenders use this information to assess the credit risk associated with a loan application and to make informed decisions about whether to approve or decline the loan, as well as to determine appropriate interest rates and terms for approved loans.    
    default_probability: float
#risk_tier is a categorical variable that classifies borrowers into different risk categories based on their predicted probability of default. common risk tiers include "Low", "Medium", "High", and "Very High". lenders use these risk tiers to quickly assess the level of risk associated with a loan application and to make informed decisions about whether to approve or decline the loan, as well as to determine appropriate interest rates and terms for approved loans. generally, borrowers classified in higher risk tiers may be subject to higher interest rates and stricter loan terms to compensate for the increased risk of default.    
    risk_tier: str
# risk_score is a numerical value that represents the overall credit risk of a borrower, typically on a scale from 300 to 850. this score is calculated based on various factors such as payment history, credit utilization, length of credit history, types of credit accounts, and recent credit inquiries. lenders use the risk score to assess the creditworthiness of a borrower and to make informed decisions about whether to approve or decline a loan application, as well as to determine appropriate interest rates and terms for approved loans. generally, a higher risk score indicates a lower credit risk and may result in more favorable loan terms for the borrower.   
    risk_score: int
# recommendation is a suggested course of action for lenders based on the predicted default probability and risk tier of a borrower. common recommendations include "Approve", "Review manually", "Additional verification required", and "Decline". lenders use these recommendations to guide their decision-making process when evaluating loan applications, helping them to determine whether to approve or decline a loan, as well as to identify cases that may require further scrutiny or additional information before making a final decision. the recommendation is typically based on predefined thresholds for default probability and risk tiers, which are determined by the lender's risk tolerance and lending policies.    
    recommendation: str
# feature_importance is a dictionary that provides insights into which features had the most influence on the model's prediction for a given loan application. it typically includes the top features and their corresponding importance scores, which indicate how much each feature contributed to the predicted default probability. lenders can use this information to understand the key factors driving the credit risk assessment and to identify areas where borrowers may need to improve their financial behavior or credit management in order to reduce their risk of default.    
    feature_importance: dict

# get_risk_tier is a helper function that takes the predicted default probability as input and returns the corresponding risk tier, recommendation, and risk score based on predefined thresholds. it categorizes borrowers into different risk tiers such as "LOW", "MEDIUM", "HIGH", and "VERY HIGH" based on their predicted probability of default, and provides recommendations for lenders on how to proceed with the loan application. the function also calculates a risk score that can be used to further assess the credit risk of the borrower. this function helps to streamline the decision-making process for lenders by providing clear guidance based on the model's predictions.
def get_risk_tier(prob: float):
# the thresholds for categorizing risk tiers and providing recommendations are based on common industry practices, but they can be adjusted based on the lender's specific risk tolerance and lending policies. the risk score is calculated in a way that higher default probabilities result in lower scores, which reflects the increased credit risk associated with higher probabilities of default. the score is also capped between 300 and 850 to align with typical credit scoring ranges used in the industry.    
    if prob < 0.15:
        return "LOW", "Approve", 850 - int(prob * 300)
    elif prob < 0.30:
        return "MEDIUM", "Review manually", 700 - int(prob * 200)
    elif prob < 0.50:
        return "HIGH", "Additional verification required", 600 - int(prob * 150)
    else:
        return "VERY HIGH", "Decline", 500 - int(prob * 100)
    
# the root endpoint ("/") provides a simple overview of the API, including its name, version, model performance, and available endpoints. this can be useful for users who want to quickly understand what the API offers and how to interact with it. the health endpoint ("/health") allows users to check the status of the API and confirm that the model is loaded and ready to make predictions. this can be helpful for monitoring the API's availability and ensuring that it is functioning properly before making prediction requests.    
@app.get("/")
# the root endpoint provides a simple overview of the API, including its name, version, model performance, and available endpoints. this can be useful for users who want to quickly understand what the API offers and how to interact with it.
def root():
# the response includes the API name, version, model performance (AUC-ROC score), and a list of available endpoints ("/predict", "/health", "/docs"). this information can help users understand the capabilities of the API and how to use it effectively.    
    return {
        "api": "Credit Risk Scoring API",
        "version": "1.0.0",
        "model": "Gradient Boosting | AUC-ROC: 0.897",
        "endpoints": ["/predict", "/health", "/docs"]
    }
# the health endpoint allows users to check the status of the API and confirm that the model is loaded and ready to make predictions. this can be helpful for monitoring the API's availability and ensuring that it is functioning properly before making prediction requests.
@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": True}
# the predict endpoint takes a loan application as input, processes it through the machine learning model, and returns a risk assessment that includes the predicted default probability, risk tier, risk score, recommendation for lenders, and feature importance. this endpoint is the core functionality of the API, allowing users to submit loan applications and receive insights into the credit risk associated with those applications based on the model's predictions.
@app.post("/predict", response_model=RiskResponse)
# the predict endpoint takes a loan application as input, processes it through the machine learning model, and returns a risk assessment that includes the predicted default probability, risk tier, risk score, recommendation for lenders, and feature importance. this endpoint is the core functionality of the API, allowing users to submit loan applications and receive insights into the credit risk associated with those applications based on the model's predictions.
def predict(loan: LoanApplication):
    input_data = [[
        loan.loan_amnt, loan.int_rate, loan.annual_inc,
        loan.dti, loan.delinq_2yrs, loan.inq_last_6mths,
        loan.open_acc, loan.revol_util, loan.total_acc, loan.emp_length
    ]]
# the input data is structured as a list of lists to match the expected format for the machine learning model, which typically requires a 2D array as input. each inner list represents a single loan application with its corresponding features, and the outer list allows for the possibility of processing multiple loan applications in a batch if needed. this format ensures that the input data is compatible with the model's requirements for making predictions.
    scaled = scaler.transform(input_data)
    prob = model.predict_proba(scaled)[0][1]
    tier, recommendation, score = get_risk_tier(prob)
# feature importance is calculated by creating a dictionary that maps each feature to its corresponding importance score from the model. the importance scores indicate how much each feature contributed to the model's prediction for the given loan application. the top 3 most important features are then extracted and included in the response to provide insights into which factors had the most influence on the credit risk assessment. this information can be valuable for lenders to understand the key drivers of risk and to identify areas where borrowers may need to improve their financial behavior or credit management.
    importances = dict(zip(features, model.feature_importances_))
    top3 = dict(sorted(importances.items(),
                key=lambda x: x[1], reverse=True)[:3])
# the response includes the predicted default probability (rounded to 4 decimal places), the risk tier, the risk score (capped between 300 and 850), the recommendation for lenders, and the top 3 most important features that influenced the model's prediction. this structured response allows users to easily understand the credit risk assessment and make informed decisions based on the insights provided by the API.
    return RiskResponse(
        default_probability=round(float(prob), 4),
        risk_tier=tier,
        risk_score=max(300, min(850, score)),
        recommendation=recommendation,
        feature_importance=top3
    )
# the sample endpoint provides example loan applications for testing and documentation purposes. it includes a low-risk application with favorable financial characteristics and a high-risk application with less favorable financial characteristics. this endpoint can be useful for users who want to see sample input data and understand how the API processes different types of loan applications to generate risk assessments. it can also serve as a reference for users when formatting their own loan applications for prediction requests.
@app.get("/sample")
def sample_applications():
    return {
        "low_risk": {
            "loan_amnt": 10000, "int_rate": 7.5,
            "annual_inc": 90000, "dti": 8.0,
            "delinq_2yrs": 0, "inq_last_6mths": 0,
            "open_acc": 10, "revol_util": 20.0,
            "total_acc": 20, "emp_length": 8
        },
        "high_risk": {
            "loan_amnt": 35000, "int_rate": 28.0,
            "annual_inc": 25000, "dti": 38.0,
            "delinq_2yrs": 3, "inq_last_6mths": 5,
            "open_acc": 15, "revol_util": 92.0,
            "total_acc": 8, "emp_length": 0
        }
    }
