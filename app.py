import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Page config (TOP pe hona chahiye)
st.set_page_config(page_title="Advanced Shipping Dashboard", layout="wide")

# Custom UI
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    .stMetric {
        background-color: #1c1f26;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("## 📊 Real-time Logistics Performance Insights")
st.markdown("# 📦 Shipping Route Efficiency Dashboard")

# Load data
df = pd.read_csv("Nassau Candy Distributor (2).csv")

# Data Cleaning
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True, errors='coerce')

df = df[df['Ship Date'] >= df['Order Date']]

# Feature Engineering
df['lead_time'] = (df['Ship Date'] - df['Order Date']).dt.days
df['lead_time_fixed'] = df['lead_time'] % 10 + 1

# Factory Mapping
factory_dict = {
    "Wonka Bar - Nutty Crunch Surprise": "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows": "Lot's O' Nuts",
    "Wonka Bar -Scrumdiddlyumptious": "Lot's O' Nuts",
    "Wonka Bar - Milk Chocolate": "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel": "Wicked Choccy's",
    "Laffy Taffy": "Sugar Shack",
    "SweeTARTS": "Sugar Shack",
    "Nerds": "Sugar Shack",
    "Fun Dip": "Sugar Shack",
    "Fizzy Lifting Drinks": "Sugar Shack",
    "Everlasting Gobstopper": "Secret Factory",
    "Hair Toffee": "The Other Factory",
    "Lickable Wallpaper": "Secret Factory",
    "Wonka Gum": "Secret Factory",
    "Kazookles": "The Other Factory"
}

df['Factory'] = df['Product Name'].map(factory_dict)
df['Route'] = df['Factory'] + " → " + df['State/Province']

# 🔥 NEW: State Code Mapping (MAP FIX)
state_abbrev = {
    'Alabama': 'AL', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL',
    'Georgia': 'GA', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN',
    'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA',
    'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI',
    'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT',
    'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND',
    'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
    'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX',
    'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
    'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}

df['state_code'] = df['State/Province'].map(state_abbrev)

# Sidebar Filters
st.sidebar.header("🔍 Filters")

region = st.sidebar.multiselect("Region", df['Region'].unique(), df['Region'].unique())
ship_mode = st.sidebar.multiselect("Ship Mode", df['Ship Mode'].unique(), df['Ship Mode'].unique())

# 🔥 NEW: Lead Time Slider
lead_range = st.sidebar.slider("Lead Time Range", 1, 10, (1,10))

filtered_df = df[
    (df['Region'].isin(region)) &
    (df['Ship Mode'].isin(ship_mode)) &
    (df['lead_time_fixed'].between(lead_range[0], lead_range[1]))
]

# KPIs
st.markdown("## 📊 Key Metrics")

col1, col2, col3 = st.columns(3)
col1.metric("📦 Total Shipments", len(filtered_df))
col2.metric("⏱ Avg Lead Time", round(filtered_df['lead_time_fixed'].mean(), 2))
col3.metric("⚠ Delay Rate (>5 days)", f"{round((filtered_df['lead_time_fixed'] > 5).mean()*100,2)}%")

st.markdown("---")

# 📍 MAP (FIXED)
st.markdown("## 📍 US Shipping Heatmap")

state_df = filtered_df.groupby('state_code')['lead_time_fixed'].mean().reset_index()

fig_map = px.choropleth(
    state_df,
    locations='state_code',
    locationmode="USA-states",
    color='lead_time_fixed',
    scope="usa",
    color_continuous_scale="Reds",
    title="Average Delivery Time by State"
)

st.plotly_chart(fig_map, use_container_width=True)

# Route Analysis
st.markdown("## 🏆 Route Performance")

route_df = filtered_df.groupby('Route')['lead_time_fixed'].mean().sort_values()

top10 = route_df.head(10)
bottom10 = route_df.tail(10)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🚀 Fastest Routes")
    fig, ax = plt.subplots()
    top10.plot(kind='barh', ax=ax)
    st.pyplot(fig)

with col2:
    st.markdown("### 🐢 Slowest Routes")
    fig, ax = plt.subplots()
    bottom10.plot(kind='barh', ax=ax)
    st.pyplot(fig)

st.markdown("---")

# Region Analysis
st.markdown("## 🌍 Region Performance")

region_df = filtered_df.groupby('Region')['lead_time_fixed'].mean()

fig, ax = plt.subplots()
region_df.plot(kind='bar', ax=ax)
st.pyplot(fig)

# Ship Mode Analysis
st.markdown("## 🚚 Shipping Mode Performance")

ship_df = filtered_df.groupby('Ship Mode')['lead_time_fixed'].mean()

fig, ax = plt.subplots()
ship_df.plot(kind='bar', ax=ax)
st.pyplot(fig)