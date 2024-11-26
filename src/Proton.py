import pyttsx3
import speech_recognition as sr
from datetime import date
import time
import webbrowser

from pynput.keyboard import Key, Controller
import pyautogui
import sys
import os
from os import listdir
from os.path import isfile, join
import smtplib
import wikipedia
import Gesture_Controller
#import Gesture_Controller_Gloved as Gesture_Controller
import app
import requests
import pyautogui
import google.generativeai as genai
import math
from datetime import datetime


from threading import Thread

genai.configure(api_key="AIzaSyA7MhLsGieP2EBtjMt5361cOyhvhWekdCY")


# -------------Object Initialization---------------
today = date.today()
r = sr.Recognizer()
keyboard = Controller()
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# ----------------Variables------------------------
file_exp_status = False
files = []
path = ''
is_awake = True  # Bot status

# ------------------Functions----------------------
def reply(audio):
    app.ChatBot.addAppMsg(audio)
    print(audio)
    engine.say(audio)
    engine.runAndWait()

def wish():
    hour = int(datetime.now().hour)
    if hour >= 0 and hour < 12:
        reply("Good Morning!")
    elif hour >= 12 and hour < 18:
        reply("Good Afternoon!")
    else:
        reply("Good Evening!")  
        
    reply("I am Proton, how may I help you?")

# Set Microphone parameters
with sr.Microphone() as source:
    r.energy_threshold = 500 
    r.dynamic_energy_threshold = False

# Audio to String
def record_audio():
    with sr.Microphone() as source:
        r.pause_threshold = 0.8
        voice_data = ''
        audio = r.listen(source, phrase_time_limit=5)

        try:
            voice_data = r.recognize_google(audio)
        except sr.RequestError:
            reply('Sorry my Service is down. Please check your Internet connection')
        except sr.UnknownValueError:
            print('Cannot recognize')
            pass
        return voice_data.lower()


def ask_gemini(question):
    try:
        # Using the correct method (hypothetically 'ask' or 'generate')
        response = genai.ask(question)  # Replace with the correct method
        return response['text']  # Or the appropriate key in the response
    except Exception as e:
        return f"Error: {str(e)}"
    





#CALCULATOR
def calculate(expression):
    try:
        # Handle advanced commands
        if 'square root' in expression:
            num = float(expression.split('square root of')[-1].strip())
            result = math.sqrt(num)
            reply(f"The square root of {num} is {result:.2f}")
            return

        elif 'power' in expression:
            base, exp = map(float, expression.split('to the power of'))
            result = math.pow(base, exp)
            reply(f"{base} to the power of {exp} is {result:.2f}")
            return

        # Handle basic arithmetic
        result = eval(expression)  # Be cautious; this evaluates any expression
        reply(f"The result of {expression} is {result:.2f}")
    except ZeroDivisionError:
        reply("Division by zero is not allowed.")
    except Exception as e:
        reply("Sorry, I couldn't calculate that. Please try again.")
        print(f"Calculation error: {e}")


# Add get_weather function here
def get_weather(city):
    API_KEY = "0f6c6da9a5f0b0988db816af7dfe492a"  # Replace with your API key
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    try:
        params = {'q': city, 'appid': API_KEY, 'units': 'metric'}
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if data['cod'] != 200:
            reply(f"Unable to find weather details for {city}.")
        else:
            weather = data['weather'][0]['description']
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            reply(f"The weather in {city} is {weather} with a temperature of {temp}°C, feels like {feels_like}°C.")
    except Exception as e:
        reply("Sorry, I couldn't fetch the weather details.")
        print(e)



# ----------------- YouTube Control Functions ------------------

# Open YouTube
def open_youtube():
    try:
        webbrowser.open("https://www.youtube.com")
        reply("Opening YouTube.")
    except Exception as e:
        reply(f"Failed to open YouTube: {e}")

# Control YouTube Playback
def youtube_control(action):
    try:
        if action == 'play' or action == 'pause':
            pyautogui.press('k')  # Toggle play/pause
            reply("Toggled play/pause on YouTube.")
        elif action == 'next':
            pyautogui.hotkey('shift', 'n')  # Next video
            reply("Skipped to the next video.")
        elif action == 'previous':
            pyautogui.hotkey('shift', 'p')  # Previous video
            reply("Went back to the previous video.")
        elif action == 'close':
            pyautogui.hotkey('ctrl', 'w')  # Close the tab
            reply("Closed YouTube.")
        else:
            reply("Unknown YouTube command.")
    except Exception as e:
        reply(f"YouTube control error: {e}")


       



# Executes Commands (input: string)
def respond(voice_data):
    
    global file_exp_status, files, is_awake, path
    print(voice_data)
    voice_data = voice_data.replace('proton', '').strip()
    app.eel.addUserMsg(voice_data)

    if not is_awake:
        if 'wake up' in voice_data:
            is_awake = True
            wish()


    elif 'weather' in voice_data:
        reply('Which city should I check for weather updates?')
        city = record_audio()  # Capture city name
        app.eel.addUserMsg(city)  # Display in GUI
        get_weather(city)  # Call get_weather function


    elif 'open youtube' in voice_data:
        open_youtube()

    elif 'play' in voice_data:
        youtube_control('play')

    elif 'pause' in voice_data:
        youtube_control('pause')

    elif 'next' in voice_data:
        youtube_control('next')

    elif 'previous' in voice_data:
        youtube_control('previous')

    elif 'close youtube' in voice_data:
        youtube_control('close')

    
    elif 'ask gemini' in voice_data:
        query = voice_data.split('ask gemini', 1)[1].strip()  # Extract the question after 'ask gemini'
        gemini_response = ask_gemini(query)  # Get the response from Gemini
        reply(ask_gemini)  # Send the response back to the user

    # STATIC CONTROLS
    elif 'hello' in voice_data:
        wish()

    elif 'what is your name' in voice_data:
        reply('My name is Proton!')

    elif 'date' in voice_data:
        reply(today.strftime("%B %d, %Y"))

    elif 'time' in voice_data:
        reply(str(datetime.datetime.now()).split(" ")[1].split('.')[0])

    elif 'search' in voice_data:
        query = voice_data.split('search', 1)[1].strip()
        reply('Searching for ' + query)
        url = 'https://google.com/search?q=' + query
        try:
            webbrowser.get().open(url)
            reply('This is what I found, Sir.')
        except:
            reply('Please check your Internet.')
    

    elif 'calculate' in voice_data or 'what is' in voice_data:
        expression = voice_data.replace('calculate', '').replace('what is', '').strip()
        app.eel.addUserMsg(expression)  # Display expression in GUI
        calculate(expression)  # Perform calculation


    
    elif 'convert temperature' in voice_data:
        parts = voice_data.split('convert temperature')[1].strip().split(' to ')
        value, from_unit = parts[0].split(' ', 1)
        to_unit = parts[1]
        result = convert_temperature(value, from_unit.lower(), to_unit.lower())
        reply(f"The conversion result is: {result}")
    
    # Distance Conversion (e.g., "convert 5 miles to kilometers")
    elif 'convert distance' in voice_data:
        parts = voice_data.split('convert distance')[1].strip().split(' to ')
        value, from_unit = parts[0].split(' ', 1)
        to_unit = parts[1]
        result = convert_distance(value, from_unit.lower(), to_unit.lower())
        reply(f"The conversion result is: {result}")
    
    # Weight Conversion (e.g., "convert 100 kilograms to pounds")
    elif 'convert weight' in voice_data:
        parts = voice_data.split('convert weight')[1].strip().split(' to ')
        value, from_unit = parts[0].split(' ', 1)
        to_unit = parts[1]
        result = convert_weight(value, from_unit.lower(), to_unit.lower())
        reply(f"The conversion result is: {result}")
    
    # Currency Conversion (e.g., "convert 100 USD to EUR")
    elif 'convert currency' in voice_data:
        parts = voice_data.split('convert currency')[1].strip().split(' to ')
        amount, from_currency = parts[0].split(' ', 1)
        to_currency = parts[1]
        result = convert_currency(float(amount), from_currency.upper(), to_currency.upper())
        reply(result)




    elif 'location' in voice_data:
        reply('Which place are you looking for?')
        temp_audio = record_audio()
        app.eel.addUserMsg(temp_audio)
        reply('Locating...')
        url = 'https://google.nl/maps/place/' + temp_audio + '/'
        try:
            webbrowser.get().open(url)
            reply('This is what I found, Sir.')
        except:
            reply('Please check your Internet.')

    elif ('bye' in voice_data) or ('by' in voice_data):
        reply("Goodbye, Sir! Have a nice day.")
        is_awake = False

    elif ('exit' in voice_data) or ('terminate' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
        app.ChatBot.close()
        sys.exit()
        
    # DYNAMIC CONTROLS
    elif 'launch gesture recognition' in voice_data:
        if Gesture_Controller.GestureController.gc_mode:
            reply('Gesture recognition is already active.')
        else:
            gc = Gesture_Controller.GestureController()
            t = Thread(target=gc.start)
            t.start()
            reply('Launched Successfully.')

    elif ('stop gesture recognition' in voice_data) or ('top gesture recognition' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
            reply('Gesture recognition stopped.')
        else:
            reply('Gesture recognition is already inactive.')
        
    elif 'copy' in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('c')
            keyboard.release('c')
        reply('Copied.')
          
    elif 'paste' in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('v')
            keyboard.release('v')
        reply('Pasted.')

    elif 'open certificates' in voice_data:
        path = 'D:\CERTIFICATES'  # Update with the correct path to Downloads
        try:
            files = listdir(path)
            filestr = ""
            for i, f in enumerate(files, start=1):
                filestr += f"{i}: {f}<br>"
            reply('Opened folder. Here are the files inside:')
            app.ChatBot.addAppMsg(filestr)
        except PermissionError:
            reply("You do not have permission to access this folder.")
        except FileNotFoundError:
            reply("The folder does not exist.")

        
    # File Navigation (Default Folder set to C://)
    elif 'list' in voice_data:
        counter = 0
        path = 'C://'
        files = listdir(path)
        filestr = ""
        for f in files:
            counter += 1
            print(str(counter) + ':  ' + f)
            filestr += str(counter) + ':  ' + f + '<br>'
        file_exp_status = True
        reply('These are the files in your root directory.')
        app.ChatBot.addAppMsg(filestr)
        
    elif file_exp_status:
        counter = 0   
        if 'open' in voice_data:
            try:
                index = int(voice_data.split(' ')[-1]) - 1
                if isfile(join(path, files[index])):
                    os.startfile(join(path, files[index]))
                    reply('Opened ' + files[index] + ' successfully.')
                    file_exp_status = False
                else:
                    # If it's a directory, list its contents
                    path = join(path, files[index])
                    files = listdir(path)
                    filestr = ""
                    for f in files:
                        counter += 1
                        filestr += str(counter) + ':  ' + f + '<br>'
                        print(str(counter) + ':  ' + f)
                    reply('Opened directory. Here are the files inside:')
                    app.ChatBot.addAppMsg(filestr)
                    
            except IndexError:
                reply('Invalid file index. Please try again.')
            except Exception as e:
                reply('You do not have permission to access this folder or the file does not exist.')
                print(e)
                                    
        if 'back' in voice_data:
            filestr = ""
            if path == 'C://':
                reply('Sorry, this is the root directory.')
            else:
                a = path.split('//')[:-2]
                path = '//'.join(a) + '//'
                files = listdir(path)
                for f in files:
                    counter += 1
                    filestr += str(counter) + ':  ' + f + '<br>'
                    print(str(counter) + ':  ' + f)
                reply('Okay.')
                app.ChatBot.addAppMsg(filestr)
                   
    else: 
        reply('I am not programmed to do this!')

# ------------------Driver Code--------------------
t1 = Thread(target=app.ChatBot.start)
t1.start()

# Lock main thread until Chatbot has started
while not app.ChatBot.started:
    time.sleep(0.5)

wish()
voice_data = None
while True:
    if app.ChatBot.isUserInput():
        # Take input from GUI
        voice_data = app.ChatBot.popUserInput()
    else:
        # Take input from Voice
        voice_data = record_audio()

    # Process voice_data
    if 'proton' in voice_data:
        try:
            respond(voice_data)
        except SystemExit:
            reply("Exit Successful.")
            break
        except Exception as e:
            print("EXCEPTION raised while closing:", e) 
            break
