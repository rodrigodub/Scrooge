import seaborn as sns
import matplotlib.pyplot as plt
# import plotly.express as px

# Import data from shared.py
from shared import df, expenses_df, categories_df, merged_df, aggregated_df

from shiny.express import input, render, ui

ui.page_opts(title="Hello sidebar!")

with ui.sidebar():
    ui.input_select("var", "Select variable", choices=["bill_length_mm", "body_mass_g"])
    ui.input_switch("species", "Group by species", value=True)
    ui.input_switch("show_rug", "Show Rug", value=True)


# @render.plot
# def hist():
#     hue = "species" if input.species() else None
#     sns.kdeplot(df, x=input.var(), hue=hue)
#     if input.show_rug():
#         sns.rugplot(df, x=input.var(), hue=hue, color="black", alpha=0.25)

@render.plot(alt="A pie chart")
def plot():
    # df = load_penguins()
    # mass = df["body_mass_g"]

    # fig, ax = plt.subplots()
    # ax.hist(mass, input.n(), density=True)

    fig, ax = plt.subplots()
    ax.pie(aggregated_df['amount'], labels=aggregated_df['category'], autopct='%1.1f%%')
    # ax.pie(merged_df['amount'])
    # ax.hist(merged_df['amount'], merged_df['category'], density=True)

    ax.set_title("Categories")

    # return fig