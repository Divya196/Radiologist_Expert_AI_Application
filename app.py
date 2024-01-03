
#from langchain.llms import OpenAI

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import streamlit as st
import os
import pathlib
import textwrap
from PIL import Image


import google.generativeai as genai


os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## Function to load OpenAI model and get respones

def get_gemini_response(input,image,prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input,image[0],prompt])
    return response.text
    

def input_image_setup(uploaded_file):
    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")


##initialize our streamlit app

st.set_page_config(page_title="Radiology Expert")

st.header("LLM Application")
input=st.text_input("Any Questions: ",key="input")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
image=""   
#if uploaded_file is not None:
#   image = Image.open(uploaded_file)
#   st.image(image, caption="Uploaded Image.", use_column_width=True)


submit1 = st.button("Tell Me About the Scan Image")
submit2 = st.button("View the Report")



input_prompt1 = """
 You are an experienced Technical Radiologist,your task is to review the provided images. 
 You are a Diagnostic radiologists, through extensive clinical work and related research, specialized in these radiology subspecialties:

Breast imaging (mammograms)
Cardiovascular radiology (heart and circulatory system)
Chest radiology (heart and lungs)
Emergency radiology
Gastrointestinal radiology (stomach, intestines and abdomen)
Genitourinary radiology (reproductive and urinary systems)
Head and neck radiology
Musculoskeletal radiology (muscles and skeleton)
Neuroradiology (brain and nervous system; head, neck and spine)
Pediatric radiology (imaging of children)

You have an excellent patient care skill.
Please share your professional evaluation on patient's condition in layman terms. 
"""

input_prompt2 = """
You are an experienced Technical Radiologist,your task is to review the provided images and give me the professional scan report for the uploaded medical imaging.
Please Use the uploaded medical imaging to diagnose,treat illnesses and give future medical care.
Highlight the abnormal and normal parts of the patient.
"""

## If ask button is clicked

if submit1:
    if uploaded_file is not None:
        image_data = input_image_setup(uploaded_file)
        response=get_gemini_response(input_prompt1,image_data,input)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload a image file to proceed.")
else:
    if uploaded_file is not None:
        image_data = input_image_setup(uploaded_file)
        response=get_gemini_response(input_prompt2,image_data,input)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload a image file to proceed.")


st.markdown("---")
st.caption("Radiology Expert offers a helping hand, to assist you in the correct interpretation and diagnosis of imaging studies.")