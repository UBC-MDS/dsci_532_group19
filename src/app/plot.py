
import numpy as np
import pandas as pd
import altair as alt
import geopandas as gpd


data = pd.read_csv("./../../data/processed/cleaned_salaries.csv")

def plot_22(xmax, con):
    

    source = data[(data["Age"]>0) & (data["Salary_USD"]<=xmax[1])]
    source = source[source["Country"] == con]
    
    alt.themes.enable("default")

    chart = alt.Chart(source).mark_rect().encode(
        x = alt.X("Age:Q", bin=alt.Bin(maxbins=60), title=None),
        y = alt.Y("Salary_USD:Q", bin=alt.Bin(maxbins=40), 
                  title="Salary in USD", axis=alt.Axis(format='~s')),
        tooltip='count()',
        color=alt.Color('count()',scale=alt.Scale(scheme='greenblue'), legend=alt.Legend(title='Tot. Records')),
    ).properties(
        title = "Rect plot by Wenjia",
        width=335,
        height=270,
    )
    
    bar = alt.Chart(source).mark_bar().encode(
        x='Age:Q',
        y='count()',
    ).properties(
        width=335,
        height=200,
    )
    
    fchart = alt.vconcat(chart, bar, spacing=0)
    
    return fchart.to_html()


def plot_12(xcon):
    
    genders = ['Male', 'Female', 'A different identity']
    source = data[(data["Country"] == xcon) & (data["GenderSelect"].isin(genders))]
    chart = alt.Chart(source).mark_boxplot().encode(
        x=alt.X("Salary_USD:Q", 
                title="Salary in USD", 
                axis=alt.Axis(format='~s'),
                scale=alt.Scale(zero=False)),
        y=alt.Y('GenderSelect', title="Gender"),
        tooltip='count()',
        color=alt.Color('GenderSelect', title='Gender')
    ).configure_legend(
        orient='bottom'
    ).properties(
        title='Boxplot by gender',
        projection={"type":'mercator'},
        width=575,
        height=180
    ).interactive()
    
    return chart.to_html()


def plot_21(value):
    
    education_order = ["Less than bachelor's degree", "Bachelor's degree", 
                       "Master's degree", "Doctoral degree"]
    
    if value == "World":
        country = data
    else:
        country = data.query("Country == @value")
        
    for idx, i in enumerate(country["FormalEducation"]):
        if i in education_order[1:]:
            continue
        else:
            print("Change")
            country["FormalEducation"].iloc[idx] = "Less than bachelor's degree"

    chart = alt.Chart(country).mark_bar().encode(
            x=alt.X("Salary_USD", bin=alt.Bin(maxbins=20), title="Salary in USD"),
            y=alt.Y("count()", title="Counts"),
            color=alt.Color("FormalEducation", sort=education_order,
            title="Education level"),
            order=alt.Order('education_order:Q')
        ).configure_legend(
            orient='bottom',
            titleFontSize=8,
            labelFontSize=8
        ).properties(
            title = "Histogram of selected country",
            width=350,
            height=180,
        ).configure_axis(
            labelFontSize=12
        )

    return chart.to_html()


def plot_11(xmax="World"):
    
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    world["name"] = world["name"].apply(lambda x:str.lower(" ".join(x.split(" ")[0:2])))
    
    world = world.loc[world["name"] != "antarctica"]
    source = data[["Country", "Salary_USD"]].groupby("Country").median().reset_index()
    source["Country"] = source["Country"].apply(lambda x:str.lower(x))
    source.rename({"Country":"name"}, axis=1, inplace=True)

    datamap = pd.merge(world, source, how='left')
    datamap['Salary_USD'] = datamap['Salary_USD'].fillna(0)
    
    chart = alt.Chart(datamap).mark_geoshape().encode( 
        color=alt.Color(field = "Salary_USD",type = "quantitative",
                        scale=alt.Scale(type = "sqrt"),
                        legend=alt.Legend(title="Salary in USD",labelFontSize = 10,symbolSize = 10,titleFontSize=10)),
        tooltip=['name:N', 'Salary_USD:Q', "alpha:Q"]
    )
    
    if xmax != "World":
        datamap["alpha"] = 1
        datamap.loc[datamap["name"] == xmax.lower(), "alpha"] = 100
        chart = chart.encode(
            opacity=alt.Opacity(field = "alpha",type = "quantitative", scale=alt.Scale(type = "sqrt")),
        )
        
    chart = chart.properties(
        title='Median Salary of The World',
        projection={"type":'mercator'},
        width=600,
        height=525,
    ).configure_axis(
        labelFontSize=10
    )    
    
    return chart.to_html()

def plot_13(DS_identity=['Yes', 'No', 'Sort of (Explain more)'], df=data.copy()):
    # Clean data
    df = df.dropna()
    df = df.query("Salary_USD < 400_000")
    df = df[df["Tenure"] != "I don't write code to analyze data"]
    
    # Filter data
    if DS_identity == None:
        DS_identity = ['Yes', 'No', 'Sort of (Explain more)']
    if not isinstance(DS_identity, list):
        DS_identity = list(DS_identity)
    df = df[df['DataScienceIdentitySelect'].isin(DS_identity)]

    # alt.themes.enable("dark")

    # Create Plot
    brush = alt.selection_interval()
    click = alt.selection_multi(fields=["Tenure"])

    points = (
        alt.Chart(df, title="Select a window for interactive coding experience count")
        .mark_circle()
        .encode(
            y=alt.Y("Country", title=None),
            x=alt.X("Salary_USD", title="Salary in USD"),
            color=alt.condition(
                brush,
                alt.Color("Tenure:N", legend=None),
                alt.value("lightgray"),
            ),
            opacity=alt.condition(click, alt.value(1.0), alt.value(0.1)),
            tooltip="EmployerIndustry",
        )
        .add_selection(brush)
    ).properties(
        width=300,
        height=680
    )

    bars = (
        alt.Chart(df, title="Click to filter the above plot!")
        .mark_bar()
        .encode(
            x="count()",
            y=alt.Y("Tenure", title="Coding Experience", sort=['More than 10 years', '6 to 10 years', '3 to 5 years', '1 to 2 years', 'Less than a year']),
            color="Tenure",
            opacity=alt.condition(click, alt.value(0.9), alt.value(0.2)),
        )
    ).transform_filter(brush)

    overall_plot = (points & bars).configure(
            background="#2c2c2c"
        ).configure_axisX(
            titleColor='white',
            titleFontSize=10,
            labelColor='white',
            labelFontSize=10
        ).configure_axisY(
            titleColor='white',
            titleFontSize=12,
            labelColor='white',
            labelFontSize=12
        ).configure_title(
            fontSize=20,
            color='white'
        ).add_selection(
            click
        )

    
    return overall_plot.to_html()

