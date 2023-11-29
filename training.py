import streamlit as st
import random

def app():
    st.header(' :crystal_ball: Running Training Generator')
    st.markdown('''
    Bored with your repeatedly dull running routine?  
    Try using training generator!  
    Choose type of running training you want below and get not your usual session.  
    Make sure to go out and complite your goal :smiling_imp:
                ''')

    # Define the training dictionary
    training_dict = {
        'Easy Run': [
            'Run for 45 minutes at a conversational pace.',
            'Recovery run for 20-30 minutes at an easy pace.',
            'Shakeout run for 15-20 minutes with smooth strides.',
            'Commute run at an easy pace for transportation.',
            'Join a group run at a conversational pace.',
            'Time-based easy run for 60 minutes at a comfortable pace.',
            'Trail run for 40 minutes at a relaxed pace.',
            'Park run with strides, including 6-8 accelerations.',
            'Fartlek easy run for 45 minutes, with short bursts of increased pace.'
        ],
        'Long Run': [
            'Run for 90 minutes at a steady, comfortable pace.',
            'Progression run for 75 minutes, starting slow and finishing faster.',
            'Aerobic threshold run for 60 minutes, just below lactate threshold.',
            'Trail long run for 2 hours on varied terrain.',
            'Group long run with friends for 2.5 hours at an easy pace.',
            'Long run with intervals, alternating between easy and faster paces.',
            'Scenic long run exploring different routes for 2 hours.',
            'Time-based long run for 2.5 hours at a steady pace.',
            'Hill long run, incorporating uphill and downhill segments for 2 hours.'
        ],
        'Speed Workout': [
            'Interval training on the track: 8x400m with 1-minute rest.',
            'Fartlek speed workout with varied paces for 45 minutes.',
            'Hill repeats: 6x1-minute hill sprints with jogging downhill recovery.',
            'Tempo run at lactate threshold pace for 30 minutes.',
            'Progression run with the last 20 minutes at a fast pace.',
            'Pyramid workout: 200m, 400m, 800m, 1600m, 800m, 400m, 200m with rest.',
            'Mile repeats on the track: 4x1 mile with 2 minutes rest.',
            'Strides and sprints: 10x100m sprints with strides in between.',
            'Cut-down run: Start slow and progressively get faster every mile.'
        ],
        'Cross-Training': [
            'Cycling for 45 minutes at a moderate intensity.',
            'Swimming for 30 minutes focusing on technique and endurance.',
            'Elliptical workout for 40 minutes with interval resistance.',
            'Rowing for 20 minutes at a steady pace.',
            'Cross-country skiing for 1 hour for a full-body workout.',
            'High-intensity interval training (HIIT) for 30 minutes.',
            'Yoga for 45 minutes to improve flexibility and core strength.',
            'Stair climbing for 20 minutes for lower body strength.',
            'Dance fitness class for 60 minutes for cardiovascular conditioning.'
        ]
    }

    # Training type selection
    selected_type = st.selectbox('Select Training Type', list(training_dict.keys()))

    # Display a random training example for the selected type
    st.markdown(f'Today for your {selected_type} you get:')
    selected_variant = random.choice(training_dict[selected_type])
    st.write(selected_variant)