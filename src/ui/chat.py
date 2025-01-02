import streamlit as st
import requests
import json

st.title("Multi Service Chat")

def process_stream(response):
    """Process streaming response and yield words"""
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    content = data.get('content', '')
                    yield content
                except json.JSONDecodeError:
                    continue

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])
        else:
            content_type, content = message["content"]
            if content_type == "text":
                st.markdown(content)
            elif content_type == "song":
                st.audio(content)
            elif content_type == "image":
                st.image(content)

# Accept user input
if prompt := st.chat_input("Ask me to generate image, song or research content..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner('Generating great content for you!'):
            try:
                response = requests.post(
                    "http://localhost:8000/generate_content",
                    json={"prompt": prompt},
                    stream=True
                )

                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')

                    if 'text/event-stream' in content_type:
                        # Handle streaming text
                        full_response = st.write_stream(process_stream(response))
                        result = ('text', full_response)
                    else:
                        # Non-streaming response
                        data = response.json()
                        result = (data['type'], data['content'])
                        # Display media content
                        if data['type'] == 'image':
                            st.image(data['content'])
                        elif data['type'] == 'song':
                            st.audio(data['content'])

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result
                    })
                    st.rerun()

                elif response.status_code == 402:
                    st.error("💰 Budget exceeded! Please check the Costs page for details.")
                else:
                    st.error("Failed to generate content")

            except Exception as e:
                st.error(f"Error: {str(e)}")

# Add some styling
st.markdown("""
<style>
    .stButton button {
        width: 100%;
    }
    .budget-warning {
        color: #ff4b4b;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)