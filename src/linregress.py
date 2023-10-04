from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



    

def linregression(dataframe : pd.DataFrame): 
    #read the dataframe 
    df = dataframe.select_dtypes(exclude='object').fillna(0)
    #select the target variable
    target_c = df['Hazardous auth']
    #select the explanatory variables with exclusion of the target variable
    features = df.loc[:,df.columns != 'Hazardous auth']
    #create a linear regress model
    model = LinearRegression()
    #fit the model to the data and predict target_c values based on input data
    model.fit(features,target_c)
    predicted_target = model.predict(features)
   #print the coefficients and intercept of the linregress
    print("Coefficients:",model.coef_)
    print("Intercept:",model.intercept_)
    return target_c,predicted_target


def visualize_linregress(target_col,predicted_target_col):
    plt.scatter(target_col,predicted_target_col) #true vs predicted
    plt.xlabel('True target column')
    plt.ylabel("Predicted target column")
    plt.title("True vs. Predicted Target values")
    plt.savefig("Linear_Regression.png")   