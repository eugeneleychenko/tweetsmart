from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import CharacterTextSplitter
import os
import openai
from dotenv import find_dotenv, load_dotenv
import requests
import json
import streamlit as st

OPENAI_API_KEY = os.getenv("OPENAI_API")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

openai_api_key = OPENAI_API_KEY

# Fetch tweet
def fetch_tweet(tweetid):
    url = "https://twitter154.p.rapidapi.com/tweet/replies"

    querystring = {"tweet_id": tweetid}

    headers = {
        "X-RapidAPI-Key": "iPxYj0SjxxHJproXNwsgNGBx5rj3yf3a",
        "X-RapidAPI-Host": "twitter154.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    json_response = response.json()

    text_values = []
    for reply in json_response["replies"]:
        text_values.append(reply["text"])

    return text_values



def main():
    load_dotenv(find_dotenv())

    st.set_page_config(page_title="Tweet Smarts", page_icon=":bird:")

    # st.header("Get More Context Around a Tweet")
    tweet = st.text_input("Enter the Tweet ID")
    # query = st.text_input("Topic of twitter thread")

    

    if tweet:
        print(tweet)
        st.write("Generating twitter research for: ", tweet)
        
        search_results = fetch_tweet(tweet)
        # urls = get_full_text(search_results)
        # data = tweet_summary(urls)
        # summaries = search(data)
        # summaries1 = find_best_article_urls(summaries)
        # summaries2 = get_content_from_urls(summaries1)

        with st.expander("Fetched Tweet"):
            st.json(search_results)
        # with st.expander("Thread"):
        #     st.info(urls)
        # with st.expander("data"):
        #     st.info(data)
        # with st.expander("summaries"):
        #     st.info(summaries)
        # with st.expander("thread"):
        #     st.info(summaries1)
        # with st.expander("thread"):
        #     st.info(summaries2)


if __name__ == '__main__':
    main()