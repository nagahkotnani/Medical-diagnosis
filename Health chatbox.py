
import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.api_core.exceptions  # Import for handling quota errors

# Configure Google Gemini API
genai.configure(api_key="AIzaSyDbfNCgu34SJxpT5sFk9VECN9NFDLcjYNk")  # Replace with your valid API key

# Initialize Gemini Model
model = genai.GenerativeModel("gemini-1.5-pro")  # Ensure this model is available

# Define doctor recommendations based on detected diseases
disease_specialist_map = {
    "Lung Cancer": "Oncologist (Lung Cancer Specialist)",
    "Breast Cancer": "Oncologist (Breast Cancer Specialist)",
    "Skin Cancer": "Dermatologist or Oncologist",
    "Diabetic Retinopathy": "Ophthalmologist",
    "Pneumonia": "Pulmonologist",
    "Tuberculosis": "Infectious Disease Specialist",
    "Fracture": "Orthopedic Surgeon",
    "Brain Tumor": "Neurosurgeon or Neuro-Oncologist"
}

# Streamlit Layout
st.set_page_config(layout="wide")  # Ensure this is the first Streamlit command

col1, col2 = st.columns([2, 1])  # Left section (Diagnosis) - 2x width, Right section (Chatbox) - 1x width

@st.cache_data  # Cache function to reduce repeated API calls
def analyze_image_with_gemini(image):
    """Send image to Gemini API for analysis and handle errors."""
    try:
        response = model.generate_content([
            image,
            "Analyze this medical image and provide possible medical insights. "
            "Detect signs of lung cancer, breast cancer, skin cancer, fractures, pneumonia, diabetic retinopathy, tuberculosis, or brain tumors. "
            "Provide a diagnosis and mention if further medical consultation is needed."
        ])
        return response.text  # Return only the text response
    except google.api_core.exceptions.ResourceExhausted:
        return "⚠️ Google Gemini API quota exhausted. Please try again later or upgrade your plan."

with col1:  # Left side for medical diagnosis
    st.title("🩺 AI-Powered Medical Diagnosis Chatbot")
    st.write("Upload an X-ray, CT scan, MRI, or eye image for AI-based analysis.")

    # Image Upload
    uploaded_file = st.file_uploader("Upload a medical image...", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # AI Analysis with error handling
        diagnosis = analyze_image_with_gemini(image)

        st.subheader("🔍 AI Diagnosis:")
        st.write(diagnosis)

        # Check if the diagnosis mentions a disease and suggest a doctor
        recommended_specialist = None
        detected_disease = None

        for disease, specialist in disease_specialist_map.items():
            if disease.lower() in diagnosis.lower():
                recommended_specialist = specialist
                detected_disease = disease
                break

        if recommended_specialist:
            st.markdown(
                f"""
                <div style="background-color: green; padding: 10px; border-radius: 10px; border-left: 5px solid red; font-size: 16px;">
                    <b>👨‍⚕️ Suggested Specialist:</b><br>
                    Based on the detected signs of <b>{detected_disease}</b>, you should consult a <b>{recommended_specialist}</b>.
                </div>
                """,
                unsafe_allow_html=True
            )

with col2:  # Right side for AI Chatbox
    st.subheader("💬 Health Chatbox")
    st.write("Describe your symptoms, and I'll provide health precautions & food recommendations.")

    user_input = st.text_input("Type your symptoms here...", placeholder="E.g. Headache, pain, fever...")

    if user_input:
        try:
            chat_response = model.generate_content([
                f"The user is experiencing: {user_input}. Provide suitable health precautions, home remedies, and foods to eat for relief."
            ])
            chat_text = chat_response.text
        except google.api_core.exceptions.ResourceExhausted:
            chat_text = "⚠️ Google Gemini API quota exhausted. Please try again later."

        st.markdown(
            f"""
            <div style="background-color: skyblue; padding: 10px; border-radius: 10px; border-left: 5px solid #0c5460; font-size: 16px;">
                <b>🩹 Precautions & Food Suggestions:</b><br>
                {chat_text}
            </div>
            """,
            unsafe_allow_html=True
        )
