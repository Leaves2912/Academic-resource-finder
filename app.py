import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
import re
import streamlit as st

st.markdown(
    """
    <style>
    * {
        font-family: 'Times New Roman', Times, serif;  
    }
    </style>
    """,
    unsafe_allow_html=True
)

def get_source_with_scraping(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.prettify()  # Formatted HTML output

def scrape_files(sub):
    results = {}

    # PowerPoint Presentations
    ppt_url = f"https://www.google.com/search?q={sub}+filetype:pptx"
    sc = get_source_with_scraping(ppt_url)
    pattern = r'https?://[^\s]+\.ppt[x]?'
    matches = re.findall(pattern, sc)
    cleaned_urls = []
    for match in matches[0:min(5, len(matches))]: 
        # Clean up spaces in the URL
        cleaned_url = match.replace(' ', '%20')
        cleaned_urls.append(cleaned_url)

    if not cleaned_urls:
        st.markdown('<p style="font-size: 24px;">No Powerpoint files available.</p>', unsafe_allow_html=True)
    else:
        # Use cleaned_urls and unquote them
        results['Powerpoint files'] = [unquote(url) for url in cleaned_urls]

    # Word Files
    doc_url = f"https://www.google.com/search?q={sub}+filetype:docx"
    sc = get_source_with_scraping(doc_url)
    pattern = r'https?://[^\s]+\.doc[x]?'
    matches = re.findall(pattern, sc)
    cleaned_urls = []
    for match in matches[0:min(5, len(matches))]:  # Start from index 1 to skip the first match
        # Clean up spaces in the URL
        cleaned_url = match.replace(' ', '%20')
        cleaned_urls.append(cleaned_url)

    if not cleaned_urls:
        st.markdown('<p style="font-size: 24px;">No Word files available.</p>', unsafe_allow_html=True)
    else:
        # Use cleaned_urls and unquote them
        results['Word files'] = [unquote(url) for url in cleaned_urls]


    # PDF Files
    pdf_url = f"https://www.google.com/search?q={sub}+filetype:pdf"
    sc = get_source_with_scraping(pdf_url)
    pattern = r'https?://[^\s]+\.pdf'
    matches = re.findall(pattern, sc)
    cleaned_urls = []
    for match in matches[0:min(5, len(matches))]:  # Limit to the first 5 matches
        # Check if the match starts with the Google URL
        if match.startswith('https://www.google.com/'):
            # Extract the part after 'imgrefurl='
            if 'imgrefurl=' in match:
                cleaned_url = match.split('imgrefurl=')[1]
            else:
                continue  # Skip this match if 'imgrefurl=' is not found
        else:
            # Clean up spaces in the URL
            cleaned_url = match.replace(' ', '%20')

        cleaned_urls.append(cleaned_url)

    if not cleaned_urls:
        st.markdown('<p style="font-size: 24px;">No PDF files available.</p>', unsafe_allow_html=True)
    else:
        # Use cleaned_urls and unquote them
        results['PDF files'] = [unquote(url) for url in cleaned_urls]


    # MIT OCW Courses
    mit_url = f"https://www.google.com/search?q={sub}+site%3Aocw.mit.edu"
    sc = get_source_with_scraping(mit_url)
    # Updated pattern to capture the URL after imgurl=
    pattern = r'https?://(?:ocw\.mit\.edu)(?:/[^/]+)*'  # Match the domain and any number of segments
    matches = re.findall(pattern, sc)

    cleaned_urls = []
    for match in matches:
        # Split the URL by '/' and limit to the first 5 segments (domain + 4 additional)
        segments = match.split('/')
        if len(segments) > 5:
            # Join only the first 5 segments to form the URL
            match = '/'.join(segments[:5])
    
        # Clean up spaces in the URL
        cleaned_url = match.replace(' ', '%20')
        # Add to the cleaned_urls list if it's unique
        if cleaned_url not in cleaned_urls:
            cleaned_urls.append(cleaned_url)
    
        # Stop if we have collected 5 unique URLs
        if len(cleaned_urls) >= 5:
            break
    if not cleaned_urls:
        st.markdown('<p style="font-size: 24px;">No MIT OCW Courses available.</p>', unsafe_allow_html=True)
    else:
        # Use cleaned_urls and unquote them
        results['MIT OCW Courses'] = [unquote(url) for url in cleaned_urls]

    # YouTube Playlists
    yt_url = f"https://www.google.com/search?q={sub}+site%3Awww.youtube.com"
    sc = get_source_with_scraping(yt_url)
    pattern = r'https\S*watch%3Fv\S*'
    matches = re.findall(pattern,sc)
    matches1 = []
    for x in matches:
        for j in range(len(x)):
            if x[j] == '&':
                matches1.append(x[:j])
                break
    matches1=list(set(matches1))
    cleaned_urls = []
    for match in matches1[0:min(5, len(matches1))]:  # Start from index 1 to skip the first match
        # Clean up spaces in the URL
        cleaned_url = match.replace(' ', '%20')
        cleaned_urls.append(cleaned_url)

    if not cleaned_urls:
        st.markdown('<p style="font-size: 24px;">No YouTube videos available.</p>', unsafe_allow_html=True)
    else:
        # Use cleaned_urls and unquote them
        results['YouTube videos'] = [unquote(url) for url in cleaned_urls]

    return results

# Streamlit UI
if 'results_found' not in st.session_state:
    st.session_state.results_found = False

# Function to handle the search action
def perform_search():
    # Get the current value of the input from session state
    search_term = st.session_state.search_term
    if search_term:
        results = scrape_files(search_term)
        if results:  # Check if results are not empty
            st.session_state.results_found = True  # Set the flag to True
            for category, links in results.items():
                st.subheader(category)
                for link in links:
                    st.write(link)
        else:
            st.session_state.results_found = False
    else:
        st.warning("Please enter a search term.")

st.markdown(
    """
    <style>
    .input-label {
        font-size: 24px;  /* Increase font size */
        margin-bottom: -35px;  /* Adjust space below the label */
        margin-top: 75px;  /* Add space above the label to move it lower */
    }
    </style>
    """,
    unsafe_allow_html=True
)

if not st.session_state.get('results_found', False):
    st.markdown("<h1 style='font-family: Times New Roman; font-size: 40px;'>Academic Resource Finder</h1>", unsafe_allow_html=True)

# Input label with a line break
st.sidebar.markdown('<div class="input-label">What would you<br>like to study today ?</div>', unsafe_allow_html=True)

# Input text box with on_change callback
st.sidebar.text_input("", key='search_term', on_change=perform_search)

# Search button (optional, can be removed if only Enter key is needed)
if st.sidebar.button("Search"):
    perform_search()