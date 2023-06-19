from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import CharacterTextSplitter
import os
import openai
from dotenv import find_dotenv, load_dotenv
import requests
import json
import streamlit as st

load_dotenv(find_dotenv())
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

openai_api_key = OPENAI_API_KEY

# Fetch tweet
def fetch_tweet(tweet):
    tweetid = tweet.split('status/')[1]
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

# summarize thread into a Google search query

def convert_to_search_query(text_values):
    # turn json into string
    response_str = json.dumps(text_values)

    # create llm to choose best articles
    llm = OpenAI(model_name="gpt-3.5-turbo", temperature=.7)
    template = """
    You are a world class journalist & researcher, you are extremely good at finding most relevant articles to certain topic;
    {response_str}
    
    Please compose the most concise Google search query to get more information on this topic. Return ONLY the Google Search query, do not include anything else.
    """

    prompt_template = PromptTemplate(
        input_variables=["response_str"], template=template)

    article_picker_chain = LLMChain(
        llm=llm, prompt=prompt_template, verbose=True)

    query = article_picker_chain.predict(response_str=response_str)

    # Convert string to list
    # url_list = json.loads(urls)
    print(query)

    return query

# serp request to get list of relevant articles

def search(query):
    url = "https://google.serper.dev/search"

    payload = json.dumps({
        "q": query
    })
    headers = {
        'X-API-KEY': SERPAPI_API_KEY,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_data = response.json()

    print("search results: ", response_data)
    return response_data


# llm to choose the best articles, and return url

def find_best_article_urls(response_data, query):
    # turn json into string
    response_str = json.dumps(response_data)

    # create llm to choose best articles
    llm = OpenAI(model_name="gpt-3.5-turbo-16k", temperature=.7)
    template = """
    You are a world class journalist & researcher, you are extremely good at find most relevant articles to certain topic;
    {response_str}
    Above is the list of search results for the query {query}.
    Please choose the best 3 articles from the list, return ONLY an array of the urls, do not include anything else; return ONLY an array of the urls, do not include anything else
    """

    prompt_template = PromptTemplate(
        input_variables=["response_str", "query"], template=template)

    article_picker_chain = LLMChain(
        llm=llm, prompt=prompt_template, verbose=True)

    urls = article_picker_chain.predict(response_str=response_str, query=query)

    # Convert string to list
    url_list = json.loads(urls)
    print(url_list)

    return url_list


# get content for each article from urls and make summary



def main():
    load_dotenv(find_dotenv())

    st.set_page_config(page_title="Tweet Smarts", page_icon=":bird:")
    st.header("Dive deeper on those smart tweets  :brain:")

    # st.header("Get More Context Around a Tweet")
    tweet = st.text_input("Enter the Tweet ID")
    # query = st.text_input("Topic of twitter thread")

    

    if tweet:
        print(tweet)
        st.write("Generating twitter research for: ", tweet)
        
        search_results = fetch_tweet(tweet)
        query_to_search = convert_to_search_query(search_results)
        results = search(query_to_search)
        articles = find_best_article_urls(results, query_to_search)
      
        

        with st.expander("Fetched Tweet"):
            st.json(search_results)
        with st.expander("Google Search query"):
            st.write(query_to_search)
        with st.expander("Google Search results"):
            st.json(results) 
        with st.expander("Best Articles"):
            st.write(articles)     


if __name__ == '__main__':
    main()