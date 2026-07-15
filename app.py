import streamlit as st
import random
from main import NewsletterGenerator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="AI Newsletter Generator",
    page_icon="📰",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .newsletter-content {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin-top: 2rem;
    }
    .topic-input {
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("📰 AI Newsletter Generator with duckduckgo 🔥")
st.markdown("""
Generate professional newsletters on any topic using Groq AI, Agno, and duckduckgo.
""")

# Example topics
example_topics = [
        "What happened in the world of AI this week?",
        "What are the latest trends in AI?",
        "Tell the Recent Model Releases",
        "Recap of Google I/O 2025",
]

# Sidebar for API keys and settings
with st.sidebar:
    st.header("🔑 API Keys")
    duckduckgo_api_key = st.text_input(
        "duckduckgo API Key",
        value=os.getenv("DUCKDUCKGO_API_KEY", ""),
        type="password",
    )
    groq_api_key = st.text_input(
        "GROQ API Key",
        value=os.getenv("GROQ_API_KEY", ""),
        type="password",
        help="Your Groq API key"
    )
    
    # Update environment variables with user input
    if duckduckgo_api_key:
        os.environ["DUCKDUCKGO_API_KEY"] = duckduckgo_api_key
    if groq_api_key:
        os.environ["GROQ_API_KEY"] = groq_api_key
    
    
    st.markdown("---")
    st.markdown("### 📚 Example Topics")
    for topic in example_topics:
        if st.button(topic, key=topic):
            st.session_state.topic = topic

# Main content area
# st.markdown("### 🎯 Enter Your Topic")
topic = st.text_input(
    "What would you like to generate a newsletter about?",
    value=st.session_state.get("topic", ""),
    placeholder="Enter a topic or select from examples",
    key="topic_input"
)


col1, col2 = st.columns(2)
with col1:
    search_limit = st.number_input(
        "Number of Articles",
        min_value=1,
        max_value=10,
        value=5,
        help="Maximum number of articles to search and analyze"
    )
with col2:
    time_range = st.selectbox(
        "Time Range",
        options=[
            ("Past hour", "qdr:h"),
            ("Past 24 hours", "qdr:d"),
            ("Past week", "qdr:w"),
            ("Past month", "qdr:m"),
            ("Past year", "qdr:y")
        ],
        format_func=lambda x: x[0],
        index=2,  # Default to "Past week"
        help="Time range for article search"
    )

# Generate button
def generate_newsletter():
    if not topic:
        st.error("Please enter a topic or select one from the examples.")
        return
    elif not duckduckgo_api_key or not groq_api_key:
        st.error("Please provide both API keys in the sidebar.")
        return
    
    with st.spinner("Generating your newsletter..."):
        try:
            # Convert the topic to a URL-safe string for use in session_id
            url_safe_topic = topic.lower().replace(" ", "-")

            # Initialize the newsletter generator
            

            # Generate the newsletter using main function
            response = NewsletterGenerator(
                topic=topic,
                search_limit=search_limit,
                time_range=time_range[1]  # Get the tbs value from the tuple
            )

            # Display the complete newsletter
            st.markdown("### 📝 Generated Newsletter")
            st.markdown(response.content)

            # Add download button
            st.download_button(
                label="📥 Download Newsletter",
                data=response.content,
                file_name=f"newsletter-{url_safe_topic}.md",
                mime="text/markdown"
            )

        except Exception as e:
            st.error(f"An error occurred while generating the newsletter: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Built with ❤️ using Streamlit and Groq AI</p>
</div>
""", unsafe_allow_html=True) 

if st.button("Generate Newsletter", type="primary"):
    generate_newsletter()