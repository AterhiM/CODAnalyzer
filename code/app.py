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