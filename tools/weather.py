import requests

def get_weather(location: str = "") -> str:
    try:
        if not location:
            location = "Newcastle"
        url = f"https://wttr.in/{location.replace(' ', '+')}?format=3"
        response = requests.get(url, timeout=5)
        return response.text.strip()
    except Exception as e:
        return f"Couldn't get weather: {str(e)}"

def get_weather_detailed(location: str = "") -> str:
    try:
        if not location:
            location = "Newcastle"
        fmt = "%l: %C, %t (feels like %f), humidity %h, wind %w, UV index %u"
        url = f"https://wttr.in/{location.replace(' ', '+')}?format={fmt}"
        response = requests.get(url, timeout=5)
        return response.text.strip()
    except Exception as e:
        return f"Couldn't get weather: {str(e)}"