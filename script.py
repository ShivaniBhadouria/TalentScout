import streamlit as st
import google.generativeai as genai
import re  # For regex validation
import random  # For generating random data
import string  # For generating random strings

# Configure API key
genai.configure(api_key="AIzaSyCgpQVfXBa98lAfaDxvTPu7MV4LWQBhYx4")

# Initialize the GenerativeModel
model = genai.GenerativeModel("gemini-2.0-flash")

# Function to initialize session state
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "candidate_info" not in st.session_state:
        st.session_state.candidate_info = {
            "full_name": None,
            "email": None,
            "phone": None,
            "years_of_experience": None,
            "desired_position": None,
            "current_location": None,
            "tech_stack": None,
        }
    if "tech_questions_generated" not in st.session_state:
        st.session_state.tech_questions_generated = False
    if "greeting_sent" not in st.session_state:
        st.session_state.greeting_sent = False
    if "tech_questions_answered" not in st.session_state:
        st.session_state.tech_questions_answered = False
    if "context" not in st.session_state:
        st.session_state.context = ""
    if "tech_questions" not in st.session_state:
        st.session_state.tech_questions = []
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0

# Function to generate AI-based responses
def get_ai_response(query):
    response = model.generate_content(query)
    return response.text

# Function to generate technical questions based on tech stack
def generate_tech_questions(tech_stack):
    questions = []
    for tech in tech_stack.split(', '):
        question = get_ai_response(f"Generate a technical interview question about just provide question not ans question should vbe in point wise {tech}.")
        questions.append(question)
    return questions

# Function to validate email
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

# Function to validate phone number
def is_valid_phone(phone):
    phone_regex = r'^\d{10}$'
    return re.match(phone_regex, phone) is not None

# Function to validate years of experience
def is_valid_experience(experience):
    return experience.isdigit() and 0 <= int(experience) <= 30

# Function to validate location
def is_valid_location(location):
    return isinstance(location, str) and location.strip() != ""

# Function to handle user input while maintaining conversation context
def handle_user_input(user_input):
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Check if the user is asking an unrelated question
    if any(keyword in user_input.lower() for keyword in ["how", "what", "why", "explain", "tell me", "define"]):
        bot_response = get_ai_response(user_input)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        return

    # Continue structured interview process
    candidate_info = st.session_state.candidate_info
    if not candidate_info["full_name"]:
        candidate_info["full_name"] = user_input
        bot_response = "Thank you! What is your email address?"
    elif not candidate_info["email"]:
        if is_valid_email(user_input):
            candidate_info["email"] = user_input
            bot_response = "Got it! What is your phone number?"
        else:
            bot_response = "Please enter a valid email address."
    elif not candidate_info["phone"]:
        if is_valid_phone(user_input):
            candidate_info["phone"] = user_input
            bot_response = "Great! How many years of experience do you have?"
        else:
            bot_response = "Please enter a valid 10-digit phone number."
    elif not candidate_info["years_of_experience"]:
        if is_valid_experience(user_input):
            candidate_info["years_of_experience"] = user_input
            bot_response = "Nice! What is your desired position?"
        else:
            bot_response = "Please enter a valid number of years of experience between 0 and 30."
    elif not candidate_info["desired_position"]:
        candidate_info["desired_position"] = user_input
        bot_response = "Got it! What is your current location?"
    elif not candidate_info["current_location"]:
        if is_valid_location(user_input):
            candidate_info["current_location"] = user_input
            bot_response = "Thanks! Please specify your tech stack (e.g., Python, React, Java, etc.)."
        else:
            bot_response = "Please enter a valid location."
    elif not candidate_info["tech_stack"]:
        candidate_info["tech_stack"] = user_input
        st.session_state.tech_questions = generate_tech_questions(user_input)
        bot_response = f"Your response has been recorded. Let's start with the technical questions. {st.session_state.tech_questions[0]}"
        st.session_state.tech_questions_generated = True
    elif st.session_state.tech_questions_generated and not st.session_state.tech_questions_answered:
        st.session_state.current_question_index += 1
        if st.session_state.current_question_index < len(st.session_state.tech_questions):
            bot_response = st.session_state.tech_questions[st.session_state.current_question_index]
        else:
            st.session_state.tech_questions_answered = True
            bot_response = "Thank you for completing the interview! We will review your responses and get back to you soon."
    else:
        bot_response = "I'm sorry, I didn't understand that. Please provide the requested information."

    st.session_state.messages.append({"role": "assistant", "content": bot_response})

# Streamlit app
def main():
    st.title("🤖 TalentScout")
    st.markdown("Welcome! I'm here to assist you with your interview process. Let's get started!", unsafe_allow_html=True)

    # Inject custom CSS for styling
    st.markdown("""
        <style>
        body {
            background-image: url('https://example.com/your-background-image.jpg');
            background-size: cover;
            color: white;
            font-family: 'Arial', sans-serif;
        }
        .chat-message {
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            max-width: 70%;
        }
        .user-message {
            background-color: #4CAF50;
            align-self: flex-end;
        }
        .assistant-message {
            background-color: #2196F3;
            align-self: flex-start;
        }
        .stChatFloatingInput > div > div > input {
            background-color: rgba(255, 255, 255, 0.8);
            color: black;
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    initialize_session_state()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(f'<div class="chat-message {message["role"]}-message">{message["content"]}</div>', unsafe_allow_html=True)

    # Send greeting message if not already sent
    if not st.session_state.greeting_sent:
        st.session_state.messages.append({"role": "assistant", "content": "Hello! Welcome to the interview process. Let's start with your full name."})
        st.session_state.greeting_sent = True
        st.rerun()

    # User input
    user_input = st.chat_input("Type your message here...")
    if user_input:
        handle_user_input(user_input)
        st.rerun()

if __name__ == "__main__":
    main()
