import streamlit as st
import pandas as pd
import plotly.express as px

# Load the dataset
@st.cache_data  # This decorator helps cache the data loading to speed up app loading
def load_data():
    return pd.read_excel("./data/african_countries_for_cod.xlsx")

data = load_data()

# App title
st.title('Market Target Selection Dashboard for COD Strategy in E-commerce in Africa')

# Sidebar for column selection
st.sidebar.header('Select Metrics')
# Let users choose which columns to filter on
selected_columns = st.sidebar.multiselect(
    'Choose columns to display sliders for:',
    options=[col for col in data.columns if pd.api.types.is_numeric_dtype(data[col]) and col != 'Country'],
    default=[col for col in data.columns if pd.api.types.is_numeric_dtype(data[col]) and col != 'Country']
)

# Initialize a DataFrame to store filtered data
filtered_data = pd.DataFrame()

# Dynamically create sliders based on selected columns and store filters
filters = {}
for col in selected_columns:
    min_val = int(data[col].min())
    max_val = int(data[col].max())
    # Store slider values in a dictionary
    filters[col] = st.sidebar.slider(f"Minimum {col}", min_val, max_val, min_val, key=col)

# Apply filters to the data
for col in selected_columns:
    if not filtered_data.empty:
        # If filtered_data is already initialized, apply filters cumulatively
        filtered_data = filtered_data[(data[col] >= filters[col])]
    else:
        # Initialize filtered_data with the first filter
        filtered_data = data[(data[col] >= filters[col])].copy()

# Display filtered data
st.subheader('Filtered Countries')
st.write(filtered_data[['Country'] + selected_columns])

# Plotting with Plotly - Horizontal Multi-Bar Chart
if not filtered_data.empty and st.checkbox('Show Plot'):
    # Melt the filtered DataFrame to make it suitable for Plotly
    melted_data = filtered_data.melt(id_vars=["Country"], var_name="Metric", value_name="Value", value_vars=selected_columns)
    # Plotting with Plotly Express
    fig = px.bar(melted_data, y="Country", x="Value", color="Metric", orientation='h', barmode='group',
                 title="Values by Country Across Selected Metrics")
    fig.update_layout(yaxis={'categoryorder':'total ascending'},
                      width=1000,
                      height=1000)
    st.plotly_chart(fig)

# Creating two columns for the layout
left_column, right_column = st.columns(2)

with left_column:
    # Sliders for weight adjustment in the left column
    st.write("Adjust the weights for calculation:")
    internet_users_weight = st.slider('Internet Users Percentage Weight', min_value=0.0, max_value=1.0, value=0.4, step=0.01)
    gdp_per_capita_weight = st.slider('GDP per Capita Weight', min_value=0.0, max_value=1.0, value=0.3, step=0.01)
    unemployment_rate_weight = st.slider('Unemployment Rate Weight', min_value=0.0, max_value=1.0, value=0.2, step=0.01)
    population_weight = st.slider('Population Weight', min_value=0.0, max_value=1.0, value=0.1, step=0.01)

# Ensure the total weight is 1
weights_sum = internet_users_weight + gdp_per_capita_weight + unemployment_rate_weight + population_weight
if round(weights_sum) != 1:
    st.error(f'The sum of weights must be 1. Sum is: {weights_sum}. Please adjust the weights.')
else:
    # Calculate a weighted score for each country with dynamic weights
    data['Score'] = (
        data['approx_percent_of_internet_users'] * internet_users_weight + 
        data['gdp_per_capita_dollars'] / 1000 * gdp_per_capita_weight + 
        (100 - data['unemployment_rate_percentage']) * unemployment_rate_weight + 
        data['population_value'] / 10000000 * population_weight
    )

    # Now sort the dataframe by the new 'Score' column in descending order to get top candidates
    top_candidates = data.sort_values(by='Score', ascending=False).reset_index(drop=True)
    top_candidates = top_candidates[
        ['Country', 'median_age_years', 'gdp_per_capita_dollars', 'merchant_marine_value', 'number_of_internet_users', 'unemployment_rate_percentage', 'population_value', 'approx_percent_of_internet_users', 'Score']
    ]

    with right_column:
        # Display the sorted top candidates
        st.write("Top Candidates Based on Score:")
        st.dataframe(top_candidates)
