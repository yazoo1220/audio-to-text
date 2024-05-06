import streamlit as st
import os
from openai import OpenAI
from docx import Document
from io import BytesIO
from pydub import AudioSegment

# OpenAIクライアントの初期化
client = OpenAI()

# AACファイルをMP3に変換する関数
def convert_aac_to_mp3(audio_data):
    with st.spinner("AACファイルをMP3に変換中..."):
        audio = AudioSegment.from_file(BytesIO(audio_data), format="aac")
        mp3_buffer = BytesIO()
        audio.export(mp3_buffer, format="mp3")
        mp3_buffer.seek(0)
        return mp3_buffer

# MP3ファイルをテキストに変換し、Docxまたはテキストとして出力する関数
def mp3_to_text(mp3_buffer):
    with st.spinner("音声をテキストに変換中..."):
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=mp3_buffer
        )
        return transcript.text

def create_docx(text):
    doc = Document()
    doc.add_paragraph(text)
    docx_buffer = BytesIO()
    doc.save(docx_buffer)
    docx_buffer.seek(0)
    return docx_buffer

# Streamlitのインターフェース設計
st.title("音声ファイルをテキストに変換")

# ファイルアップロード
uploaded_file = st.file_uploader("AACファイルをアップロードしてください", type=['aac'])
output_format = st.selectbox("出力フォーマットを選択", ["テキスト", "Docx"])

if uploaded_file is not None:
    # AACをMP3に変換
    mp3_buffer = convert_aac_to_mp3(uploaded_file.read())
    
    # MP3をテキストに変換
    text = mp3_to_text(mp3_buffer)
    
    # テキストをマークダウンとして整形して表示
    if output_format == "テキスト":
        st.markdown("### 変換されたテキスト")
        st.markdown(text.replace("\n", "  \n"))
        st.download_button(
            label="テキストファイルとしてダウンロード",
            data=text,
            file_name="transcript.txt",
            mime="text/plain"
        )
    elif output_format == "Docx":
        docx_buffer = create_docx(text)
        st.download_button(
            label="Word文書としてダウンロード",
            data=docx_buffer,
            file_name="transcript.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
