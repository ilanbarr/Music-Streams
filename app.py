import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
file_path = 'Most Streamed Spotify Songs 2024.csv'
df = pd.read_csv(file_path, encoding='ISO-8859-1').drop_duplicates(['Artist', 'Track'])
df = df[df['Artist'] != 'xSyborg']

# Convert stream columns to numeric, removing commas
platforms = ['Spotify Streams', 'YouTube Views', 'TikTok Views', 'Soundcloud Streams']
for platform in platforms:
    df[platform] = df[platform].replace({',': ''}, regex=True).astype(float)

# Add year
df['Release Year'] = pd.to_datetime(df['Release Date']).dt.year

# Set page configuration
st.set_page_config(page_title='Most Streamed Songs Dashboard', layout='wide')
st.title('Most Streamed Songs Dashboard')

# Overview Metrics
st.header('Overview')
total_tracks = len(df)
total_streams = df['Spotify Streams'].sum()
st.metric('Total Tracks', total_tracks)
st.metric('Total Streams', f"{total_streams:,.0f}")

# Top 50 Table
st.header('Top 50 Streamed Songs by Platform')

# Platform selection dropdown
selected_platform = st.selectbox('Select Platform', platforms)

top_50_data = df.nlargest(50, selected_platform)
st.dataframe(top_50_data[['Track', 'Artist', 'Release Year', selected_platform]], use_container_width=True)

# Histogram of top songs by year
st.header('Histogram of Top Songs by Release Year')
top_50_years = top_50_data['Release Year'].value_counts().reset_index()
top_50_years.columns = ['Release Year', 'Number of Songs']
top_50_years = top_50_years.sort_values(by='Release Year')

year_chart = alt.Chart(top_50_years).mark_bar().encode(
    x=alt.X('Release Year:O', title='Release Year'),
    y=alt.Y('Number of Songs:Q', title='Number of Songs'),
    color=alt.Color('Release Year:N', scale=alt.Scale(scheme='category20b'), legend=None)
).properties(
    width=700,
    height=400
)

st.altair_chart(year_chart, use_container_width=True)

# Top artists by platform
top_artists_by_platform = df.groupby('Artist')[selected_platform].sum().sort_values(ascending=False).head(10)
top_artists_by_platform_df = top_artists_by_platform.reset_index()

st.header(f'Top Artists by {selected_platform}')
artist_chart = alt.Chart(top_artists_by_platform_df).mark_bar().encode(
    x=alt.X('Artist', sort='-y'),
    y=alt.Y(selected_platform),
    color=alt.Color('Artist', legend=None)
).properties(width=700, height=400)
st.altair_chart(artist_chart, use_container_width=True)

# Sum streams for each platform
platform_totals = df[platforms].sum().reset_index()
platform_totals.columns = ['Platform', 'Streams']

# Create a bar chart to compare platforms
platform_chart = alt.Chart(platform_totals).mark_bar().encode(
    x=alt.X('Platform:N', title='Platform'),
    y=alt.Y('Streams:Q', title='Total Streams'),
    color=alt.Color('Platform:N', scale=alt.Scale(scheme='category20b')),
    tooltip=['Platform', 'Streams']
).properties(
    width=600,
    height=400,
    title='Total Streams by Platform'
).configure_axis(
    labelFontSize=12,
    titleFontSize=14
).configure_title(
    fontSize=16
)

st.altair_chart(platform_chart, use_container_width=True)

# Explicit vs Non-Explicit tracks
st.header('Explicit vs Non-Explicit Tracks')
explicit_group = df.groupby('Explicit Track')[platforms].mean().reset_index()
explicit_group_melted = explicit_group.melt(id_vars='Explicit Track', value_vars=platforms, var_name='Platform', value_name='Average Streams')

chart = alt.Chart(explicit_group_melted).mark_bar().encode(
    x=alt.X('Platform:N', title='Platform'),
    y=alt.Y('Average Streams:Q', title='Average Streams'),
    color=alt.Color('Explicit Track:N', 
                    scale=alt.Scale(domain=[0, 1], range=['#1f77b4', '#ff7f0e']), 
                    title='Explicit Track'),
    xOffset=alt.XOffset('Explicit Track:N')
).properties(
    width=600,
    height=400,
    title='Average Streams per Platform: Explicit vs. Non-Explicit Tracks'
).configure_axis(
    labelFontSize=12,
    titleFontSize=14
).configure_title(
    fontSize=16
)

st.altair_chart(chart, use_container_width=True)

# New visualizations

# 1. Spotify Streams distribution
st.header('Distribution of Spotify Streams')
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(df['Spotify Streams'].dropna(), kde=True, log_scale=True, ax=ax)
ax.set_title('Distribution of Spotify Streams (Log Scale)')
ax.set_xlabel('Spotify Streams')
ax.set_ylabel('Count')
st.pyplot(fig)

# 2. Track Score distribution
st.header('Distribution of Track Scores')
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(df['Track Score'], kde=True, ax=ax)
ax.set_title('Distribution of Track Scores')
ax.set_xlabel('Track Score')
ax.set_ylabel('Count')
st.pyplot(fig)

# 3. Explicit vs Non-Explicit tracks pie chart
st.header('Proportion of Explicit vs Non-Explicit Tracks')
explicit_counts = df['Explicit Track'].value_counts()
fig, ax = plt.subplots(figsize=(8, 8))
ax.pie(explicit_counts, labels=['Non-Explicit', 'Explicit'], autopct='%1.1f%%')
ax.set_title('Proportion of Explicit vs Non-Explicit Tracks')
st.pyplot(fig)

# 4. Release Year vs Average Spotify Streams
st.header('Average Spotify Streams by Release Year')
yearly_streams = df.groupby('Release Year')['Spotify Streams'].mean().sort_index()
fig, ax = plt.subplots(figsize=(12, 6))
yearly_streams.plot(kind='line', marker='o', ax=ax)
ax.set_title('Average Spotify Streams by Release Year')
ax.set_xlabel('Year')
ax.set_ylabel('Average Spotify Streams')
st.pyplot(fig)

# 5. Correlation Matrix
st.header('Correlation Matrix of Numeric Features')
numeric_cols = ['Spotify Streams', 'Track Score', 'Spotify Popularity', 
                'Apple Music Playlist Count', 'Deezer Playlist Count', 'Amazon Playlist Count']
correlation_matrix = df[numeric_cols].corr()
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5, ax=ax)
ax.set_title('Correlation Matrix of Numeric Features')
st.pyplot(fig)

# 6. Track Score vs Spotify Streams scatter plot
st.header('Track Score vs Spotify Streams')
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(df['Track Score'], df['Spotify Streams'], alpha=0.5)
ax.set_title('Track Score vs Spotify Streams')
ax.set_xlabel('Track Score')
ax.set_ylabel('Spotify Streams')
ax.set_yscale('log')
st.pyplot(fig)

# 7. Summary statistics
st.header('Summary Statistics for Key Numeric Columns')
st.write(df[numeric_cols].describe())

# 8. Time series of top tracks
st.header('Release Date and Spotify Streams of Top 10 Tracks')
top_tracks = df.nlargest(10, 'Spotify Streams')
fig, ax = plt.subplots(figsize=(12, 6))
for _, track in top_tracks.iterrows():
    ax.plot(track['Release Date'], track['Spotify Streams'], 'o', label=track['Track'])
ax.set_title('Release Date and Spotify Streams of Top 10 Tracks')
ax.set_xlabel('Release Date')
ax.set_ylabel('Spotify Streams')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
st.pyplot(fig)

st.write("Data Exploration Complete")