import streamlit as st
from streamlit_option_menu import option_menu
import home, strava, training, calculator

st.set_page_config(page_title='Running-helper space',
                   page_icon=':running:')

hide_streamlit_style = """
            <style>
            MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):

        self.apps.append({
            'title': title,
            'function': func
        })

    def run():
        with st.sidebar:        
            app = option_menu(
                menu_title='App Menu',
                options=['home', 'strava', 'training', 'calculator'],
                icons=['house', 'graph-up-arrow', 'calendar2-week', 'calculator'],
                menu_icon='gear',
                default_index=0,
                styles={
                    'container': {'padding': '5!important', 'background-color': 'black'},
        'icon': {'color': 'white', 'font-size': '23px'}, 
        'nav-link': {'color':'white','font-size': '20px', 'text-align': 'left', 'margin':'0px', '--hover-color': 'blue'},
        'nav-link-selected': {'background-color': '#02ab21'},})

        if app == 'home':
            home.app()
        if app == 'strava':
            strava.app()
        if app == 'training':
            training.app() 
        if app == 'calculator':
            calculator.app()            
    
    run()
