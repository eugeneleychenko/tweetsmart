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
X_RAPIDAPI_KEY = os.getenv("X-RAPIDAPI-KEY")

openai_api_key = OPENAI_API_KEY

# Fetch tweet
def fetch_tweet(tweet):
    tweetid = tweet.split('status/')[1]
    url = "https://twitter154.p.rapidapi.com/tweet/replies"

    
    querystring = {"tweet_id": tweetid}

    headers = {
        "X-RapidAPI-Key": X_RAPIDAPI_KEY,
        "X-RapidAPI-Host": "twitter154.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    json_response = response.json()

    text_values = []
    for reply in json_response["replies"]:
        text_values.append(reply["text"])

    return text_values


# A lot has been borrowed from https://github.com/JayZeeDesign/autonomous-researcher/blob/main/app.py
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
def get_content_from_urls(url_list):   
    # use unstructuredURLLoader
    loader = UnstructuredURLLoader(urls=url_list)
    data = loader.load()

    return data

def summarise(data, query):
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=3000, chunk_overlap=200, length_function=len)
    text = text_splitter.split_documents(data)    

    llm = OpenAI(model_name="gpt-3.5-turbo-16k", temperature=.7)
    template = """
    {text}
    You are a world class journalist, and you will try to summarise the text above in order to create a research report about {query}
    Please follow all of the following rules:
    1/ Make sure the content is engaging, informative with good data.
    2/ Make sure the content is not too long, it should be no more than 10 BULLET points
    3/ The content should address the {query} topic very well
    4/ The audience will be filled with people that are capable so include actionable advice.
    5/ The content needs to be written in a way that is easy to read and understand
    6/ The content needs to give audience actionable advice & insights too

    SUMMARY:
    """

    prompt_template = PromptTemplate(input_variables=["text", "query"], template=template)

    summariser_chain = LLMChain(llm=llm, prompt=prompt_template, verbose=True)

    summaries = []

    for chunk in enumerate(text):
        summary = summariser_chain.predict(text=chunk, query=query)
        summaries.append(summary)

    print(summaries)
    return summaries



# main
def main():
    load_dotenv(find_dotenv())

    
    st.header("Dive Deeper on Those Smart :bird: Tweets  :brain:")

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
        data = get_content_from_urls(articles)
        summary = summarise(data, query_to_search)
      
        

        with st.expander("Fetched Tweet"):
            st.json(search_results)
        with st.expander("Google Search query"):
            st.write(query_to_search)
        with st.expander("Google Search results"):
            st.json(results) 
        with st.expander("Best Articles"):
            st.write(articles)  
        with st.expander("Write up"):
            st.info(summary)      


if __name__ == '__main__':
    main()