from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from PIL import Image, ImageOps
import uuid

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at root
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", "r") as file:
        html_content = file.read()
    return html_content

# Morse code dictionary
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 
    'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 
    'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 
    'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..', '1': '.----', 
    '2': '..---', '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...', 
    '8': '---..', '9': '----.', '0': '-----', ', ': '--..--', '.': '.-.-.-', '?': '..--..', 
    '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-'
}

# Define input model for text to morse
class TextInput(BaseModel):
    text: str

# Endpoint for Morse code conversion
@app.post("/text-to-morse")
async def text_to_morse(input: TextInput):
    text = input.text.upper()
    morse_code = " ".join(MORSE_CODE_DICT.get(char, char) for char in text)
    return {"morse_code": morse_code}

# Endpoint for image inversion
@app.post("/invert-image")
async def invert_image(file: UploadFile = File(...)):
    image = Image.open(file.file)
    inverted_image = ImageOps.invert(image.convert("RGB"))

    # Save the inverted image to a temporary file
    inverted_image_path = "static/inverted_image.png"
    inverted_image.save(inverted_image_path, format="PNG")

    return FileResponse(inverted_image_path, media_type="image/png", filename="inverted.png")

# Endpoint for uploading audio file and providing URL for playback
@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    audio_id = str(uuid.uuid4())
    audio_path = f"static/{audio_id}_{file.filename}"
    
    with open(audio_path, "wb") as audio_file:
        audio_file.write(await file.read())

    audio_url = f"/static/{audio_id}_{file.filename}"
    return {"audio_url": audio_url}
