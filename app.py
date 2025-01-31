import os
import streamlit as st
import glob

# Set the base directory for narrations
NARRATIONS_DIR = "narration"

st.title("🎙️ Generated Narrations")

# List available subfolders
subfolders = [
    f
    for f in os.listdir(NARRATIONS_DIR)
    if os.path.isdir(os.path.join(NARRATIONS_DIR, f))
]

if not subfolders:
    st.warning("No narration subfolders found!")
else:
    # Select a subfolder
    selected_folder = st.selectbox("Select a Narration Category:", subfolders)

    # Get list of audio files in the selected folder
    folder_path = os.path.join(NARRATIONS_DIR, selected_folder)
    audio_files = sorted(
        glob.glob(os.path.join(folder_path, "*.wav"))
    )

    if not audio_files:
        st.warning("No audio files found in this category!")
    else:
        # Display each audio file with a player
        for audio_file in audio_files:
            st.subheader(os.path.basename(audio_file))
            st.audio(audio_file)
