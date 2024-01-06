
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import streamlit as st
import os
import io
import pathlib
import textwrap
from PIL import Image
import pydicom 
import numpy as np
import google.generativeai as genai


os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def dicom_to_jpg(dicom_filepath):
  """Converts a DICOM file to a JPG file.

  Args:
    dicom_file: The path to the DICOM file.

  Returns:
    A PIL Image object containing the converted JPG image.
  """

  # Read the DICOM file.
  dicom_image = pydicom.dcmread(dicom_filepath)

  # Get the pixel data.
  pixel_data = dicom_image.pixel_array

  # Convert the pixel data to RGB.
  rgb_pixel_data = np.stack([pixel_data, pixel_data, pixel_data], axis=2)

  # Create a PIL Image object from the RGB pixel data.Return the PIL Image object.
  image = Image.fromarray(rgb_pixel_data, mode='RGB')

  #To save it as a jpg or png image
  image.save('image.jpg')



def save_dicom_file(dicom_file, folder_path):
  """Saves a DICOM file to a folder.

  Args:
    dicom_file: The DICOM file to save.
    folder_path: The path to the folder where the DICOM file should be saved.
  """

  # Create the folder if it does not exist.
  if not os.path.exists(folder_path):
    os.makedirs(folder_path)

  # Save the DICOM file to the folder.
  dicom_file.save_as(os.path.join(folder_path, dicom_file.filename))


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
input=st.text_input("Input Prompt : ",key="input")
uploaded_file = st.file_uploader("Upload a DICOM file", type="dcm")

image=""   


submit=st.button("CONVERT TO JPG FILE")
## If ask button is clicked
if submit:
    if uploaded_file is not None:
        dicom_file = pydicom.read_file(uploaded_file)
        save_dicom_file(dicom_file, "dicom_files")
        dicom_to_jpg(os.path.join("dicom_files", dicom_file.filename))
        st.write("Jpg image file is ready to proceed.")

    else:
        st.write("Please upload a image file to proceed.")

downloaded_file = st.file_uploader("Choose the jpg image now...", type="jpg")

submit1 = st.button("Tell Me About the Scan Image")
submit2 = st.button("View the Report")



input_prompt1 = """
 You are an experienced Technical Radiologist,your task is to review the provided images along with the input prompt. 
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
Highlight the abnormal and normal parts of the patient and also answerfor the input prompt
"""



if submit1:
    if downloaded_file is not None:
        image_data = input_image_setup(downloaded_file)
        response=get_gemini_response(input_prompt1,image_data,input)
        st.subheader("The Response is")
        st.write(response)
      
    else:
        st.write("Please upload a image file to proceed.")
else:
    if downloaded_file is not None:
        image_data = input_image_setup(downloaded_file)
        response=get_gemini_response(input_prompt2,image_data,input)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload a image file to proceed.")

#function to load gemini pro model and get response
chat_model = genai.GenerativeModel("gemini-pro")
chat = chat_model.start_chat(history=[])

#later -->power of streamlit to store all the history in the form of seesions and stored in DB


def get_gemini_response_chat(question):
    response = chat.send_message(question,stream= True)
    return response


#initialize session state for chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []


chat_input = st.text_input("ASK YOUR QUESTIONS ",key="chat_input")
submit3 = st.button("GO")

if submit3 and chat_input:
    response = get_gemini_response_chat(input)

    #add user query and response to session chat history
    st.session_state['chat_history'].append(("YOU: ",chat_input))
    st.subheader("The response is")

    for chunk in response:
        st.write(chunk.text)
        st.session_state['chat_history'].append(("BOT: ",chunk.text))


st.subheader("The Chat history is")

for role,text in st.session_state['chat_history']:
    st.write(f"{role}:{text}")


st.markdown("---")
st.caption("Radiology Expert offers a helping hand, to assist you in the correct interpretation and diagnosis of imaging studies.")