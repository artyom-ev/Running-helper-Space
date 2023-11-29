import streamlit as st
import re
import pandas as pd


def app():
    st.header(' :memo: Running calculator page')

    def calculate_pace(distance_km, time):
        """
        Calculate running pace given distance in kilometers and time in the format 'hh:mm:ss'.

        Parameters:
        distance_km (float): Distance in kilometers.
        time (str): Time in the format 'hh:mm:ss'.

        Returns:
        float: Running pace in minutes per kilometer.
        """
        hours, minutes, seconds = map(int, time.split(':'))
        total_minutes = hours * 60 + minutes + seconds / 60
        pace = total_minutes / distance_km
        return pace

    def format_pace(pace):
        """
        Format a running pace in minutes per kilometer to the format typically seen on training watches.

        Parameters:
        pace (float): Running pace in minutes per kilometer.

        Returns:
        str: Formatted running pace in the format 'mm:ss' (minutes:seconds) per kilometer.
        """
        minutes = int(pace)
        seconds = int((pace % 1) * 60)
        return f"{minutes:02d}:{seconds:02d}"

    def parse_pace(pace_str):
        """
        Parse a formatted running pace in the format 'mm:ss' (minutes:seconds) per kilometer to a float pace in minutes per kilometer.

        Parameters:
        pace_str (str): Formatted running pace in the format 'mm:ss' (minutes:seconds) per kilometer.

        Returns:
        float: Running pace in minutes per kilometer.
        """
        minutes, seconds = map(int, pace_str.split(':'))
        pace = minutes + seconds / 60
        return pace

    def calculate_splits(distance, split_length, pace_actual):
        """
        Calculate the time it takes to complete each split given the total distance, split length, and actual pace.

        Parameters:
        distance (int): Total distance in meters.
        split_length (int): Length of each split in meters.
        pace_actual (str): Actual running pace in the format 'mm:ss' (minutes:seconds) per kilometer.

        Returns:
        pandas.DataFrame: A DataFrame containing the splits and the corresponding time to complete each split.
        """
        splits = []
        for i in range(split_length, distance, split_length):
            splits.append(i)
        if distance not in splits:
            splits.append(distance)

        table = pd.DataFrame(splits, columns=['Splits'])
        pace = parse_pace(pace_actual)
        table['Time'] = table['Splits'] * pace / 1000
        table['Time'] = table['Time'].apply(format_pace)
        table.reset_index(drop=True, inplace=True)
        table.rename_axis('N', inplace=True)
        table.index += 1

        return table
    
    
    st.subheader('Pace calculator')
    # Time input
    time_input = st.text_input('Enter time (hh\:mm\:ss) :', value='00:00:00')
    # Distance input
    distance_input = st.number_input('Enter distance (km):')
    # Processing input data
    if st.button('Calculate pace'):
        # Check if time and distance were entered
        if time_input and distance_input:
            # Check time format using regular expression
            time_pattern = r'^\d{2}:\d{2}:\d{2}$'
            if not re.match(time_pattern, time_input):
                st.warning('Incorrect time format. Please use the format hh:mm:ss')
                return
            # Calculate pace
            running_pace = calculate_pace(distance_input, time_input)
            # Calculate formatted pace
            formatted_pace = format_pace(running_pace)
            # Output the result
            st.write(f'Your pace: {formatted_pace} min/km')
        else:
            st.warning('Please enter time and distance')
         
    st.markdown('<hr>', unsafe_allow_html=True) # Divider
    
    
    st.subheader('Splits calculator')
    # Input fields
    distance = st.number_input('Total Distance (m):', value=10000)
    split_length = st.number_input('Split Length (m):', value=1000)
    pace_actual = st.text_input('Pace (mm\:ss)', value='4:11')
    # Calculate splits
    if st.button('Calculate splits'):
        table = calculate_splits(distance, split_length, pace_actual)
        st.dataframe(table)