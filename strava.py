import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os, gzip
import zipfile
import glob
import fitdecode
from pathlib import Path
import shutil


def app():
    st.header(':microscope: Strava activities exploration')
    st.markdown('''
    To see your training analysis you need to do a few steps:  
    1. go to your strava settings  
    2. find page of your account settings  
    3. find paragraph about "downloading data or deleting account"  
    4. press "begin" button and choose request for downloading your account data
    5. when you'll get your data upload here __only__:  
        * CSV file of your activities 
        * ZIP folder with your fit files

    ''')
    uploaded_files = st.file_uploader('Choose a file', type=['zip', 'csv'], accept_multiple_files=True)
    # Button to execute code after files are uploaded
    if st.button('Execute Code'):
        if len(uploaded_files) == 2:
            os.mkdir('uploads')
            # Save ZIP archive and CSV file to the local directory
            def save_uploadedfile(uploaded_file):
                with open(os.path.join('uploads', uploaded_file.name),'wb') as f:
                    f.write(uploaded_file.getbuffer())
            
            for uploaded_file in uploaded_files:
                file_details = {'Filename':uploaded_file.name,'FileType':uploaded_file.type,'FileSize':uploaded_file.size}
                save_uploadedfile(uploaded_file)
                st.success(f'{uploaded_file.name} uploaded successfully!')
                

            st.subheader('This is the head of your data')
            usecols = ['Activity ID', 'Activity Date', 'Activity Name', 'Activity Type', 'Max Heart Rate', 'Relative Effort',
                        'Filename', 'Moving Time', 'Distance.1', 'Elevation Gain', 'Average Heart Rate']
            df = pd.read_csv(
                            'uploads/activities.csv',
                            usecols=usecols,
                            parse_dates=['Activity Date'],
                            header=0
                            )
            # Add day, week, month, quarter, year columns
            names = ['Day', 'Week', 'Month', 'Quarter', 'Year']
            periods = ['D', 'W', 'M', 'Q', 'y']
            for n, p in zip(names, periods):
                df.insert(2, n, df['Activity Date'].dt.to_period(p).astype(str))
            # Convert moving time from seconds to hours
            df.insert(0, 'Moving Time (hr)', df['Moving Time'] / 3600)
            # Convert distance from meters to kilometers
            df.insert(0, 'Distance (km)', df['Distance.1'] / 1000)
            # Calculate average speed
            df.insert(0, 'Average Speed (km/hr)', df['Distance (km)'] / df['Moving Time (hr)'])
            st.dataframe(df)
            # Print date bounds of the data
            st.write(f'Ranges from {df.Day.min()} to {df.Day.max()}')

            
            st.subheader('Vizualize your total cumulative distance covered')
            # Define a time period by which you want to split your overall time: 'Year', 'Quarter', 'Month', 'Week', or 'Day'
            time_unit_km = 'Month'
            # Group by time_unit_km and activity type
            df_km = df.groupby(by=[time_unit_km, 'Activity Type'], as_index=False).agg(
                count=('Distance (km)', 'count'),
                total_distance_km=('Distance (km)', 'sum'),
                avg_distance_km=('Distance (km)', 'mean'),
            )
            # This will ensure there is point on the plot for each combination
            activities = df_km['Activity Type'].unique()
            activitie_months = df_km[time_unit_km].unique()
            for a in activities:
                temp = df_km.loc[df_km['Activity Type'] == a]
                for t in activitie_months:
                    if not (temp[time_unit_km] == t).any():
                        new_row = pd.Series(
                            [t, a, 0, 0, 0],
                            index=df_km.columns,
                        )
                        df_km = pd.concat([df_km, new_row.to_frame().T], ignore_index=True)
            # Find and exclude activities with <= 1 km total covered you can increase or decrease this cutoff based on your data
            kms = df_km.groupby(by=['Activity Type'], as_index=False).sum()
            kms = kms[kms['total_distance_km'] > 1]
            # For each activity and time period, calculate the cumulative sum of kms
            csum = df_km.loc[df_km['Activity Type'].isin(kms['Activity Type'])]
            x = pd.Series(dtype=float)
            csum.sort_values(by=['Activity Type', time_unit_km], inplace=True)
            for a in csum['Activity Type'].unique():
                temp = csum.loc[csum['Activity Type'] == a].sort_values(by=[time_unit_km])
                x = pd.concat([x, temp['total_distance_km'].cumsum()])
            csum['csum_km'] = x
            
            # For the plot tile
            total_km = round(df_km['total_distance_km'].sum())
            # Plot a stacked area plot
            fig_km = px.area(
                csum,
                x=time_unit_km,
                y='csum_km',
                color='Activity Type',
                title=f'My {total_km} Kilometers on Strava!',  # Set title text
                hover_data={  # Define variables for hover text
                    'csum_km': ':.1f',
                    'count': ':f',
                    'total_distance_km': ':.1f',
                    'avg_distance_km': ':.1f',
                },
                labels=dict(  # Define labels for variables
                    count='Number of activities',
                    avg_distance_km='Average kms per activity',
                    total_distance_km='Total kms covered',
                    csum_km='Cumulative kms covered',
                ),
                color_discrete_sequence=px.colors.qualitative.Bold,  # Define color swatch
            )
            # Set max allowed of ticks on x and y axes
            fig_km.update_xaxes(nticks=20)
            fig_km.update_yaxes(nticks=15)
            # Adjust the size and layout
            fig_km.update_layout(
                autosize=False,
                width=700,
                height=500,
                template='plotly_white',  # Others options: 'plotly', 'plotly_dark', 'ggplot2', 'seaborn', 'simple_white'
                title={'y': 0.9, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},  # Center title
            )
            st.plotly_chart(fig_km)

            
            st.subheader('Vizualize your total time spent in each activity')
            # Define a time unit: 'Year', 'Quarter', 'Month', 'Week', or 'Day'
            time_unit_bar = 'Month'
            # Group by time_unit_bar and activity type
            df_hr = df.groupby(by=[time_unit_bar, 'Activity Type'], as_index=False).agg(
                count=('Moving Time (hr)', 'count'),
                total_hr_spent=('Moving Time (hr)', 'sum'),
                avg_hr_spent=('Moving Time (hr)', 'mean'),
            )
            
            # For the plot tile
            total_hr = round(df_hr['total_hr_spent'].sum())
            # Plot a stacked bar plot
            fig_hr = px.bar(
                df_hr,
                x=time_unit_bar,
                y='total_hr_spent',
                color='Activity Type',
                title=f'My {total_hr} hours on Strava!',  # Set title text
                hover_data={  # Define variables for hover text
                    'count': ':f',
                    'total_hr_spent': ':.1f',
                    'avg_hr_spent': ':.1f',
                },
                labels=dict(  # Define labels for variables
                    total_hr_spent='Total hrs spent',
                    count='Number of activities',
                    avg_hr_spent='Average hrs spent per activity',
                ),
                color_discrete_sequence=px.colors.qualitative.Bold,  # Define color swatch
            )
            # Set max allowed of ticks on x and y axes
            fig_hr.update_xaxes(nticks=20)
            fig_hr.update_yaxes(nticks=15)
            # Adjust the size and layout
            fig_hr.update_layout(
                autosize=False,
                width=700,
                height=500,
                template='plotly_white',  # Others options: 'plotly', 'plotly_dark', 'ggplot2', 'seaborn', 'simple_white'
                legend=dict(  # Move the legend to the bottom
                    orientation='h',
                    yanchor='bottom',
                    y=-0.6,
                    xanchor='right',
                    x=1,
                    title=None,  # Remove legend title
                ),
                title={'y': 0.9, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},  # Center title
            )
            st.plotly_chart(fig_hr)


            st.subheader('Vizualize locations of your activities')
            # Get .fit.gz files referenced in activities.csv
            listed_files = df['Filename']
            listed_files = df['Filename'].loc[listed_files.str.contains('.fit.gz', na=False)]
            # Extract files from activities.zip
            with zipfile.ZipFile('uploads/activities.zip', 'r') as zip_ref:
                zip_ref.extractall('uploads/')
            # Get .fit.gz files available locally and referenced in activities.csv
            available_files = glob.glob(os.path.join('uploads/activities/*.fit.gz'))
            files = listed_files.tolist() and available_files
            # Unzip those .fit.gz files
            for f in files:
                with gzip.open(f, 'rb') as f_in:
                    with open('uploads/activities/' + Path(f).stem, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            # Remove .gz extension
            files = [x[:-3] for x in files]
            st.write(f'Number of FIT files in your data: {len(files)}')
            # Read each FIT file and get the first pair of coordinates (if it exist)
            # Initialize a DataFrame to hold coordinates
            coords = pd.DataFrame(columns=['Filename (decompressed)', 'timestamp', 'lat', 'long'])
            for f in files:
                with fitdecode.FitReader(f) as fit_file:
                    for frame in fit_file:
                        if (isinstance(frame, fitdecode.records.FitDataMessage) and frame.name == 'record'):
                            # See if there are coordinates
                            try:
                                new_row = pd.Series(
                                    [f, frame.get_value('timestamp'), frame.get_value('position_lat') / 11930465, frame.get_value('position_long') / 11930465],
                                    index=coords.columns,
                                )
                                coords = pd.concat([coords, new_row.to_frame().T], ignore_index=True)
                                
                                break
                            except Exception:
                                pass
            # Enrich coords with activities.csv data into a new DataFrame, cdf
            coords['Filename (decompressed)'] = coords['Filename (decompressed)'].str.replace('uploads/', '')
            df['Filename (decompressed)'] = df['Filename'].str.replace('.gz', '')  # To match on filename
            cdf = pd.merge(
                left=df,
                right=coords,
                how='inner',
                on=['Filename (decompressed)'],
            )
            
            # Plot a scatter plot map
            fig_map = px.scatter_geo(
                cdf,
                lat='lat',
                lon='long',
                size='Distance (km)',
                color='Activity Type',
                projection='natural earth',
                title='Mapping my workouts!',  # Set title
                opacity=0.75,  # Adjust opacity of dots
                color_discrete_sequence=px.colors.qualitative.Bold,  # Define color swatch
                custom_data=[  # Variables for the hover text
                    'Activity Name',
                    'Activity Date',
                    'Distance (km)',
                    'Average Speed (km/hr)',
                    'Elevation Gain',
                ],
            )
            # Center your map based on your coordinates
            fig_map.update_geos(fitbounds='locations')
            # Customize hover text
            fig_map.update_traces(
                hovertemplate='Activity Name: %{customdata[0]}<br>'
                'Activity date: %{customdata[1]|%Y-%m-%d}<br>'
                'Distance (km): %{customdata[2]:.1f}<br>'
                'Average Speed (km/hr): %{customdata[3]:.1f}<br>'
                'Elevation gain: %{customdata[4]:.1f}'
            )
            # Adjust the size and layout
            fig_map.update_layout(
                autosize=False,
                width=750,
                height=500,
                legend=dict(  # Move the legend to the bottom
                    orientation='h',
                    yanchor='bottom',
                    y=-0.1,
                    xanchor='right',
                    x=1,
                    title=None,  # Remove legend title
                ),
                title={'y': 0.85, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},  # Center title
            )
            # Customize the colors of the map
            fig_map.update_geos(
                resolution=50,
                showcountries=True, countrycolor='forestgreen',
                showcoastlines=True, coastlinecolor='darkolivegreen',
                showland=True, landcolor='darkseagreen',
                showocean=True, oceancolor='lightcyan',
                showlakes=True, lakecolor='LightBlue',
                showrivers=True, rivercolor='LightBlue',
            )
            st.plotly_chart(fig_map)

            shutil.rmtree('uploads')
            
        else:
            st.warning('Upload CSV file of your summary activities and ZIP file with all activities before executing the code.')
        

    
    
   
