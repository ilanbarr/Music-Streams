import streamlit as st
import pandas as pd
import altair as alt
import altair as alt
import numpy as np

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



# Assuming df is your DataFrame with the 'Spotify Streams' column
st.header('Distribution of Spotify Streams')

# Calculate the bin edges using logarithmic scale
min_streams = df['Spotify Streams'].min()
max_streams = df['Spotify Streams'].max()
log_bins = np.logspace(np.log10(max(1, min_streams)), np.log10(max_streams), num=50)

# Create a histogram using the log-scaled bins
hist, bin_edges = np.histogram(df['Spotify Streams'], bins=log_bins)

# Create a DataFrame for the histogram data
hist_df = pd.DataFrame({
    'Spotify Streams': bin_edges[:-1],
    'Count': hist
})

# Create the Altair chart
spotify_streams_chart = alt.Chart(hist_df).mark_bar().encode(
    x=alt.X('Spotify Streams:Q', 
            scale=alt.Scale(type='log', base=10),
            axis=alt.Axis(title='Spotify Streams (log scale)')),
    y=alt.Y('Count:Q', title='Frequency'),
    tooltip=[alt.Tooltip('Spotify Streams:Q', title='Spotify Streams', format=',.0f'),
             alt.Tooltip('Count:Q', title='Frequency')]
).properties(
    width=700,
    height=400,
    title='Distribution of Spotify Streams'
)

st.altair_chart(spotify_streams_chart, use_container_width=True)

st.header('Distribution of Track Scores')

# Ensure there are no missing or erroneous values in the 'Track Score' column
df = df.dropna(subset=['Track Score'])

track_score_chart = alt.Chart(df).transform_density(
    density='Track Score',
    as_=['Track Score', 'Density'],
    extent=[df['Track Score'].min(), df['Track Score'].max()],
    counts=False,  # Set to True if you want count density
).mark_area().encode(
    x=alt.X('Track Score:Q', title='Track Score'),
    y=alt.Y('Density:Q', title='Density'),
    tooltip=[alt.Tooltip('Track Score:Q', title='Track Score'),
             alt.Tooltip('Density:Q', title='Density')]
).properties(
    width=700,
    height=400,
    title='Distribution of Track Scores'
)

st.altair_chart(track_score_chart, use_container_width=True)


# st.altair_chart(track_score_chart, use_container_width=True)
st.header('Proportion of Explicit vs Non-Explicit Tracks')

# Prepare the data for the pie chart
explicit_counts = df['Explicit Track'].value_counts().reset_index()
explicit_counts.columns = ['Explicit Track', 'Count']
explicit_counts['Explicit Track'] = explicit_counts['Explicit Track'].replace({0: 'Non-Explicit', 1: 'Explicit'})

# Create the Altair pie chart
explicit_pie_chart = alt.Chart(explicit_counts).mark_arc(innerRadius=50).encode(
    theta=alt.Theta(field="Count", type="quantitative"),
    color=alt.Color(field="Explicit Track", type="nominal"),
    tooltip=[alt.Tooltip('Explicit Track:N', title='Track Type'), 
             alt.Tooltip('Count:Q', title='Count')]
).properties(
    width=400,
    height=400,
    title='Proportion of Explicit vs Non-Explicit Tracks'
)

st.altair_chart(explicit_pie_chart, use_container_width=True)

st.header('Average Spotify Streams by Release Year')

# Ensure 'Release Year' is properly parsed as an integer
df['Release Year'] = pd.to_datetime(df['Release Date']).dt.year

# Calculate the average Spotify Streams per Release Year
yearly_streams = df.groupby('Release Year')['Spotify Streams'].mean().reset_index()

# Create the Altair line chart
yearly_streams_chart = alt.Chart(yearly_streams).mark_line(point=True).encode(
    x=alt.X('Release Year:O', title='Release Year', axis=alt.Axis(format='d')),
    y=alt.Y('Spotify Streams:Q', title='Average Spotify Streams'),
    tooltip=[alt.Tooltip('Release Year:O', title='Release Year'), 
             alt.Tooltip('Spotify Streams:Q', title='Avg Spotify Streams')]
).properties(
    width=700,
    height=400,
    title='Average Spotify Streams by Release Year'
)

st.altair_chart(yearly_streams_chart, use_container_width=True)

# # 5. Correlation Matrix
#st.header('Correlation Matrix of Numeric Features')

# Define the numeric columns to include in the correlation matrix
numeric_cols = ['Spotify Streams', 'Track Score', 'Spotify Popularity', 
                'Apple Music Playlist Count', 'Deezer Playlist Count', 'Amazon Playlist Count']

# Calculate the correlation matrix
correlation_matrix = df[numeric_cols].corr()

# Transform the correlation matrix into a tidy format
correlation_matrix = correlation_matrix.stack().reset_index()
correlation_matrix.columns = ['Feature 1', 'Feature 2', 'Correlation']

# Create the Altair chart
correlation_matrix_chart = alt.Chart(correlation_matrix).mark_rect().encode(
    x=alt.X('Feature 1:O', title='Feature 1'),
    y=alt.Y('Feature 2:O', title='Feature 2'),
    color=alt.Color('Correlation:Q', scale=alt.Scale(scheme='redblue', domain=(-1, 1))),
    tooltip=[alt.Tooltip('Feature 1:N', title='Feature 1'),
             alt.Tooltip('Feature 2:N', title='Feature 2'),
             alt.Tooltip('Correlation:Q', title='Correlation')]
).properties(
    width=700,
    height=400,
    title='Correlation Matrix of Numeric Features'
)

st.altair_chart(correlation_matrix_chart, use_container_width=True)

# # 6. Track Score vs Spotify Streams scatter plot
# st.header('Track Score vs Spotify Streams')

# Create the Altair scatter plot
scatter_chart = alt.Chart(df).mark_circle(size=60).encode(
    x=alt.X('Track Score:Q', title='Track Score'),
    y=alt.Y('Spotify Streams:Q', title='Spotify Streams', scale=alt.Scale(type='log')),
    color=alt.Color('Track Score:Q', scale=alt.Scale(scheme='viridis'), legend=None),
    tooltip=[alt.Tooltip('Track:N', title='Track'),
             alt.Tooltip('Artist:N', title='Artist'),
             alt.Tooltip('Track Score:Q', title='Track Score'),
             alt.Tooltip('Spotify Streams:Q', title='Spotify Streams', format=',')]
).properties(
    width=700,
    height=400,
    title='Track Score vs Spotify Streams'
)

st.altair_chart(scatter_chart, use_container_width=True)

# # 7. Summary statistics
# st.header('Summary Statistics for Key Numeric Columns')
# st.write(df[numeric_cols].describe())

st.header('Release Date and Spotify Streams of Top 10 Tracks')

# Convert 'Release Date' to datetime if it's not already
df['Release Date'] = pd.to_datetime(df['Release Date'], errors='coerce')

# Filter to get the top 10 tracks by Spotify Streams
top_tracks = df.nlargest(10, 'Spotify Streams')[['Track', 'Release Date', 'Spotify Streams']]

# Create the Altair time series chart
time_series_chart = alt.Chart(top_tracks).mark_line(point=True).encode(
    x=alt.X('Release Date:T', title='Release Date'),
    y=alt.Y('Spotify Streams:Q', title='Spotify Streams', scale=alt.Scale(type='log')),
    color=alt.Color('Track:N', legend=alt.Legend(title="Track")),
    tooltip=[alt.Tooltip('Track:N', title='Track'),
             alt.Tooltip('Release Date:T', title='Release Date'),
             alt.Tooltip('Spotify Streams:Q', title='Spotify Streams', format=',')]
).properties(
    width=800,
    height=400,
    title='Release Date and Spotify Streams of Top 10 Tracks'
)

st.altair_chart(time_series_chart, use_container_width=True)

st.write("Data Exploration Complete")
