
import pandas as pd
import matplotlib.pyplot as plt








def hazardous_pie_chart(df : pd.DataFrame):
        total_count = len(df[df["Hazardous auth"]])
        hsub_in_food = len(df[df["Hazardous auth"] & df["food_contact"]])
        hsub_no_food = total_count - hsub_in_food
        
        chart_data = [hsub_in_food,hsub_no_food]
        labels = ["In contact","No contact"]
        colors = {'red','blue'}
        plt.pie(chart_data,labels=labels,colors=colors,autopct='%.2f')
        plt.title("Percentage of Hazardous substances in contact with food")
        plt.show()