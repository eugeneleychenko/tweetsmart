import requests
import json
import streamlit as st

st.title('Be Tweet Smart')
st.text_input('Enter Tweet ID')

def get_full_text(json_data):
    full_text_list = []
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if key == "full_text":
                full_text_list.append(value)
            else:
                full_text_list.extend(get_full_text(value))
    elif isinstance(json_data, list):
        for item in json_data:
            full_text_list.extend(get_full_text(item))
    return full_text_list

url = "https://twitter135.p.rapidapi.com/v2/TweetDetail/"
querystring = {"id":"1668750254680965121"}
headers = {
    "X-RapidAPI-Key": "iPxYj0SjxxHJproXNwsgNGBx5rj3yf3a",
    "X-RapidAPI-Host": "twitter135.p.rapidapi.com"
}
response = requests.get(url, headers=headers, params=querystring)
response_json = response.json()
full_text_values = get_full_text(response_json)
st.text(full_text_values)