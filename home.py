import streamlit as st

def app():
    st.header(':house_with_garden: Home page')
    
    st.subheader('Running-helper space is an application created for users to provide help with their training procces')
    
    st.markdown('''
    In the application menu you can navigate yourself between different pages:
    - strava - page where you can upload your strava running activities and vizualize them:
        + :triangular_ruler: &nbsp; what distance you've covered in each of your sport types
        + :hourglass_flowing_sand: &nbsp; how many hours you spend in each of your sport types
        + :world_map: &nbsp; find interesting locations of you training sessions
    - training - page where you can diversify your everyday training routine
    - calculator - page where you can calculate valuable parameters for your runs and races
                ''')
