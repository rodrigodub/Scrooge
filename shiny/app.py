import pandas as pd
# import seaborn as sns
import plotly.express as px
# import matplotlib.pyplot as plt
from shiny.express import input, render, ui
from shinywidgets import render_widget

# Import data from shared.py
# from shared import df, expenses_df, categories_df, merged_df, aggregated_df
from shared import merged_df

# Shiny UI
ui.page_opts(title="Family Expenses")
ui.input_date_range("daterange", "Date range", start=merged_df["date"].min())

# with ui.sidebar():
#     # ui.input_date_range("daterange", "Date range", start="2020-01-01")
#     ui.input_date_range("daterange", "Date range", start=merged_df["date"].min())
#     # merged_df["date"].min()
#     ui.input_select("var", "Select variable", choices=["bill_length_mm", "body_mass_g"])
#     ui.input_switch("species", "Group by species", value=True)
#     ui.input_switch("show_rug", "Show Rug", value=True)

# @render.plot(alt="A pie chart")
# def plot():
#     # Matplotlib
#     fig, ax = plt.subplots()
#     ax.pie(aggregated_df['amount'], labels=aggregated_df['category'], autopct='%1.1f%%')
#     ax.set_title("Categories")

# # Get the selected date range from the input
# start_date, end_date = input.daterange()
# # Convert start_date and end_date to datetime64 if necessary
# start_date = pd.to_datetime(start_date)
# end_date = pd.to_datetime(end_date)

# TODO: can I not repeat the start_date, end_date below and make the two widgets (plot & data grid) to filter each other

@render_widget
def plot():
    # Get the selected date range from the input
    start_date, end_date = input.daterange()
    # Convert start_date and end_date to datetime64 if necessary
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    #
    consolidated_df = merged_df[(merged_df["date"] >= start_date) &
                                (merged_df["date"] <= end_date)].groupby('category', as_index=False)['amount'].sum()
    total = consolidated_df["amount"].sum()
    # Plotly
    # fig = px.pie(merged_df[(merged_df["date"] >= start_date) &
    #                        (merged_df["date"] <= end_date)].groupby('category', as_index=False)['amount'].sum(),
    fig = px.pie(consolidated_df,
                 # aggregated_df,
                 values='amount', names='category', labels={'amount': 'Amount'},
                 title=f'Total Expenses: \n${total:.2f}',
                 hole=0.3)  # Optional: add a hole for a donut chart
    return fig

@render.data_frame
def expenses_df():
    # Get the selected date range from the input
    start_date, end_date = input.daterange()
    # Convert start_date and end_date to datetime64 if necessary
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    # return render.DataGrid(merged_df)
    return render.DataGrid(merged_df[(merged_df["date"] >= start_date) &
                                     (merged_df["date"] <= end_date)].sort_values("date", ascending=False))