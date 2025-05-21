import streamlit as st
import requests
import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime

# Load API keys from .env file
load_dotenv()
weather_api_key = os.getenv("WEATHER_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=gemini_api_key)

def get_weather_data(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"
    response = requests.get(url)
    return response.json()

def get_weekly_forecast(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={weather_api_key}&units=metric"
    response = requests.get(url)
    return response.json()

def generate_weather_description(data):
    try:
        temperature = data['main']['temp']
        description = data['weather'][0]['description']
        city_name = data['name']
        prompt = (
            f"The current weather in {city_name} is {description} "
            f"with a temperature of {temperature:.1f} °C. Explain this dramaticaly for a general audience in 5 line."
        )
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(prompt)
        # Fix here: access the text correctly
        generated_text = response.candidates[0].content.parts[0].text.strip()
        return generated_text
    except Exception as e:
        st.warning(f"AI generation error: {e}")
        # Fallback text if AI fails
        return f"The current weather in {city_name} is {description} with a temperature of {temperature:.1f} °C."


def display_weekly_forecast(data):
    try:
        st.subheader("📅 Weekly Weather Forecast")
        displayed_dates = set()
        for entry in data['list']:
            date = datetime.fromtimestamp(entry['dt']).strftime('%A, %B %d')
            if date not in displayed_dates:
                displayed_dates.add(date)
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"**{date}**")
                with col2:
                    st.write(entry['weather'][0]['description'].capitalize())
                with col3:
                    st.write(f"Min: {entry['main']['temp_min']:.1f}°C")
                with col4:
                    st.write(f"Max: {entry['main']['temp_max']:.1f}°C")
    except Exception as e:
        st.error(f"Error displaying weekly forecast: {e}")

def main():
    st.sidebar.title("Weather Forecasting with Gemini AI")
    city = st.sidebar.text_input("Enter city name", "Chennai")

    if not weather_api_key or not gemini_api_key:
        st.error("Missing API keys. Please check your .env file.")
        return

    if st.sidebar.button("Get Weather"):
        st.title(f"🌍 Weather update for {city}")
        with st.spinner("Fetching weather data..."):
            weather_data = get_weather_data(city)
            if weather_data.get("cod") != 200:
                st.error("Invalid city name or API error!")
                return
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🌡 Temperature", f"{weather_data['main']['temp']:.1f} °C")
                st.metric("💧 Humidity", f"{weather_data['main']['humidity']}%")
            with col2:
                st.metric("💨 Pressure", f"{weather_data['main']['pressure']} hPa")
                st.metric("🍃 Wind Speed", f"{weather_data['wind']['speed']} m/s")
            
            # Generate and display AI description
            ai_description = generate_weather_description(weather_data)
            st.write(ai_description)
            
            lat, lon = weather_data['coord']['lat'], weather_data['coord']['lon']
            forecast_data = get_weekly_forecast(lat, lon)
            if forecast_data.get("cod") == "200":
                display_weekly_forecast(forecast_data)
            else:
                st.error("Error fetching weekly forecast data!")

if __name__ == "__main__":
    main()
