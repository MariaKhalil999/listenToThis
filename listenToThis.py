import praw
from dotenv import load_dotenv
import os
import streamlit as st
from streamlit_tags import st_tags
import re

load_dotenv()

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USERNAME = os.getenv("REDDIT_USERNAME")

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=f'script:listentothis:v1.0 (by /u/{USERNAME})'
)

music_subs = [
    "ListenToThis",
    "MusicRecommendations",
    "MusicSuggestions",
    "IndieMusic",
    "HipHopHeads",
    "EDM",
    "Metal",
    "Rock",
    "Popheads",
    "Jazz",
    "ClassicalMusic",
    "KPop",
    "MusicCritique",
    "Songwriting",
    "BedroomBands",
    "FutureBeats",
    "ExperimentalMusic"
    # Add more
]



st.subheader("Search for subreddits to browse")

# Store selected subreddits in session
if "selected_subs" not in st.session_state:
    st.session_state.selected_subs = []

# Suggestions come from list of music subs
suggestions = music_subs  # full list by default

# Display suggestions as tags with autocomplete
st_tags(
    label='Select subreddits to browse',
    text='Type to search and press enter',
    value=st.session_state.selected_subs,
    suggestions=suggestions,
    maxtags=20,
    key="selected_subs"
)


colors = ["darkcyan", "mediumpurple", "tan", "orange", "crimson", "teal", "olive"]

def display_colored_subs(subs: list[str], colors: list[str]):
    if not subs:
        st.write("Currently browsing: None")
        return

    pills = []
    for i, sub in enumerate(subs):
        color = colors[i % len(colors)]  # cycle through colors
        pills.append(f'<span style="background-color:{color}; color:white; padding:4px 8px; border-radius:12px; margin-right:4px;">{sub}</span>')

    st.markdown(f"**Currently browsing:** {' '.join(pills)}", unsafe_allow_html=True)

# Usage
display_colored_subs(st.session_state.selected_subs, colors)


def fetch_posts(subreddit_name, limit):
    try:
        subreddit = reddit.subreddit(subreddit_name)
        posts = []
        for post in subreddit.new(limit=limit):
            if post.removed_by_category or post.selftext == "[deleted]" or post.author is None:
                continue

            posts.append({
                "title": post.title,
                "url": post.url,
                "flair": post.link_flair_text or "",
                "score": post.score
            })

        return posts
    
    except Exception as e:
        st.error(f"Error fetching posts from r/{subreddit_name}: {e}")
        return []


def get_youtube_thumbnail(url):
    """
    Extract the YouTube video ID from a URL and return the thumbnail URL.
    """
    # Regex to match video ID from standard YouTube URLs
    match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
    if match:
        video_id = match.group(1)
        return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    return None

# UI display functions


def colorize_multiselect_options(colors: list[str]) -> None:
    rules = ""
    n_colors = len(colors)

    for i, color in enumerate(colors):
        rules += f""".stMultiSelect div[data-baseweb="select"] span[data-baseweb="tag"]:nth-child({n_colors}n+{i+1}){{background-color: {color}; color: white;}}"""

    st.markdown(f"<style>{rules}</style>", unsafe_allow_html=True)

# UI display
st.set_page_config(layout="wide")
st.title("🎵 Reddit Music Suggestions")

limit = st.slider("Number of posts per subreddit:", 1, 20, 5)
gradient_percent = int((limit - 1) / (20 - 1) * 100)
with open("styles.css") as f:
    slider_css = f.read()
slider_css = slider_css.replace("{GRADIENT_PERCENT}", str(gradient_percent))
st.markdown(f"<style>{slider_css}</style>", unsafe_allow_html=True)


genres = st.multiselect(
    "What are your favorite genres?",
    options=["rock", "metal", "punk", "alternative", "pop", "hip-hop", "electronic"],
    max_selections=10,
    default = ["rock", "metal", "punk"],
    help = "You can type to search for more genres.",
)
colors = ["darkcyan", "mediumpurple", "tan", "orange", "crimson", "teal", "olive"]

colorize_multiselect_options(colors)

for subreddit_name in st.session_state.selected_subs:
    st.header(f"r/{subreddit_name}")
    posts = fetch_posts(subreddit_name, limit=limit)

    count = 0

    for post in posts:
        st.markdown(f"**{post['title']}** (Score: {post['score']})")

        youtube_thumbnail = get_youtube_thumbnail(post['url'])
        if youtube_thumbnail:
            st.image(youtube_thumbnail, width=320)
        
        st.markdown(f"[Link]({post['url']})")
        if post['flair']:
            st.markdown(f"*Flair: {post['flair']}*")
        st.markdown("---")

        count += 1

    if count == 0:
        st.write("No valid posts found.")


    print("\n")