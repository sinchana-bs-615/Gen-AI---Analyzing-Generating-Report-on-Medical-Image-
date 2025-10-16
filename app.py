# app.py
import os
from PIL import Image as PILImage
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.media import Image as AgnoImage
import streamlit as st

# Read API key from environment (safer than hardcoding)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
if not GOOGLE_API_KEY:
    raise ValueError("⚠️ Please set your Google API Key in the environment variable GOOGLE_API_KEY")

# Initialize the Medical Agent
medical_agent = Agent(
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[DuckDuckGoTools()],
    markdown=True
)

# Medical Analysis Query (keeps same instructions you provided)
query = """
You are a highly skilled medical imaging expert with extensive knowledge in radiology and diagnostic imaging. Analyze the medical image and structure your response as follows:

### 1. Image Type & Region
- Identify imaging modality (X-ray/MRI/CT/Ultrasound/etc.).
- Specify anatomical region and positioning.
- Evaluate image quality and technical adequacy.

### 2. Key Findings
- Highlight primary observations systematically.
- Identify potential abnormalities with detailed descriptions.
- Include measurements and densities where relevant.

### 3. Diagnostic Assessment
- Provide primary diagnosis with confidence level.
- List differential diagnoses ranked by likelihood.
- Support each diagnosis with observed evidence.
- Highlight critical/urgent findings.

### 4. Patient-Friendly Explanation
- Simplify findings in clear, non-technical language.
- Avoid medical jargon or provide easy definitions.
- Include relatable visual analogies.

### 5. Research Context
- Use DuckDuckGo search to find recent medical literature.
- Search for standard treatment protocols.
- Provide 2-3 key references supporting the analysis.

Ensure a structured and medically accurate response using clear markdown formatting.
"""

def analyze_medical_image(image_path):
    """Processes and analyzes a medical image using AI."""
    image = PILImage.open(image_path)
    width, height = image.size
    aspect_ratio = width / height if height != 0 else 1
    new_width = 500
    new_height = int(new_width / aspect_ratio)
    resized_image = image.resize((new_width, new_height))

    temp_path = "temp_resized_image.png"
    resized_image.save(temp_path)

    agno_image = AgnoImage(filepath=temp_path)

    try:
        response = medical_agent.run(query, images=[agno_image])
        # If the response object structure differs, adjust accordingly
        return getattr(response, "content", str(response))
    except Exception as e:
        return f"⚠️ Analysis error: {e}"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# Streamlit UI
st.set_page_config(page_title="Medical Image Analysis", layout="centered")
st.title("🩺 Medical Image Analysis Tool 🔬")
st.markdown(
    """
    Welcome to the **Medical Image Analysis** tool! 📸
    Upload a medical image (X-ray, MRI, CT, Ultrasound, etc.), and the AI-powered system will analyze it.
    """
)

st.sidebar.header("Upload Your Medical Image:")
uploaded_file = st.sidebar.file_uploader("Choose a medical image file", type=["jpg", "jpeg", "png", "bmp", "gif"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    if st.sidebar.button("Analyze Image"):
        with st.spinner("🔍 Analyzing the image... Please wait."):
            # Save uploaded file to temporary path
            ext = uploaded_file.type.split("/")[-1] if "/" in uploaded_file.type else "png"
            image_path = f"temp_image.{ext}"
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            report = analyze_medical_image(image_path)
            st.subheader("📋 Analysis Report")
            st.markdown(report, unsafe_allow_html=True)

            if os.path.exists(image_path):
                os.remove(image_path)
else:
    st.warning("⚠️ Please upload a medical image to begin analysis.")
