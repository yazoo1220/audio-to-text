import streamlit as st
import os
from openai import OpenAI
from docx import Document
from io import BytesIO
from pydub import AudioSegment

# OpenAIクライアントの初期化
client = OpenAI()

# AACファイルをMP3に変換する関数
def convert_audio_to_mp3(audio_data, file_type):
    with st.spinner(f"{file_type.upper()}ファイルをMP3に変換中..."):
        audio = AudioSegment.from_file(BytesIO(audio_data), format=file_type)
        if file_type != "mp3":
            mp3_buffer = BytesIO()
            audio.export(mp3_buffer, format="mp3")
            mp3_buffer.seek(0)
            return mp3_buffer
        else:
            return BytesIO(audio_data)  # MP3の場合はそのまま利用

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
uploaded_file = st.file_uploader("音声ファイルをアップロードしてください", type=['aac', 'mp3', 'm4a'])
output_format = st.selectbox("出力フォーマットを選択", ["テキスト", "Docx"])

if uploaded_file is not None:
    # アップロードされたファイルのMIMEタイプから正確なフォーマットを抽出
    file_type = uploaded_file.type.split('/')[1]  # MIMEタイプから 'aac' を取得する

    # 音声をMP3に変換（必要な場合）
    mp3_buffer = convert_audio_to_mp3(uploaded_file.read(), file_type)
    
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
