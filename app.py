import streamlit as st
from pydub import AudioSegment
import os
import azure.cognitiveservices.speech as speechsdk
import time
import openai


def recognize_from_audioFile(audiofile):
    """
    音声テキスト変換
    """
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))

    # speech_config.speech_recognition_language="en-US"
    speech_config.speech_recognition_language="ja-JP"

  
    from_file(speech_config, audiofile)


def from_mic(speech_config):
    """
    マイクからリアルタイムに音声テキスト変換を行う
    """
    # speech_config = speechsdk.SpeechConfig(subscription="YourSpeechKey", region="YourSpeechRegion")
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    print("Speak into your microphone.")
    result = speech_recognizer.recognize_once_async().get()
    print(result.text)


def from_file(speech_config, audiofile):
    """
    音声ファイルをテキストに変換
    """
    done = False
    # result = ""
    def stop_cb(evt):
        """
        音声テキスト変換停止コールバック
        """
        print('CLOSING on {}'.format(evt))
        speech_recognizer.stop_continuous_recognition()
        nonlocal done
        done = True

    def recongizedHandler(evt):
        """
        音声テキスト変換終了コールバック
        """
        global g_result
        g_result += evt.result.text


    audio_input = speechsdk.audio.AudioConfig(filename=audiofile)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)
    speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
    speech_recognizer.recognized.connect(recongizedHandler)
    speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)
    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(.5)


def summarize(transcript):
    """
    テキスト文章を要約
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")

    completion = openai.Completion.create(
        model="text-davinci-003",
        # prompt="Summarize this for a second-grade student:\n\n " + transcript,
        # prompt="Convert my short hand into a first-hand account of the meeting:\n\n " + transcript,
        prompt="Please summarize the following meeting minutes:\n\n " + transcript,
        temperature=0,
        max_tokens=1000,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0)
    return completion.choices[0].text

def formatSummary(summary):
    summary_change= summary.maketrans({'。':'。<br>','.':".<br>"})
    return summary.translate(summary_change)

g_result = ""
st.title("音声テキスト変換と要約アプリ")

st.markdown("### データ準備")
input_option  = st.selectbox("入力データの選択",
             ("直接入力","音声をテキストに変換して要約する"))
input_data = None

if input_option == "直接入力":
    input_data  = st.text_area('こちらにテキストを入力してください','議事録を入力してください')
    if(input_data!= "議事録を入力してください"):
        summary = formatSummary(summarize(input_data))
        st.write("### テキスト要約結果:")
        st.write(summary, unsafe_allow_html=True)
    else:
        st.write("### テキスト要約結果:")
        st.write("議事録を入力してください")
elif input_option  == "音声をテキストに変換して要約する":
    uploaded_file = st.file_uploader("mp3ファイルをアップロードしてください",["mp3"])
    if uploaded_file is not None:
        # Load the mp3 file
        audio = AudioSegment.from_mp3(uploaded_file)
        fileName = uploaded_file.name.split(".")[0]
        wavFileName =  fileName + ".wav"

        # Specify the frequency (in Hz) for the wav file
        frequency = 48000

        if not os.path.exists(wavFileName):
            # Export the wav file with the specified frequency
            audio.export(wavFileName, format="wav", parameters=["-ar", str(frequency)])

        #play auido
        st.audio(uploaded_file)

        with st.spinner('変換中...'):
            recognize_from_audioFile(wavFileName)
        st.success('Done!')
        st.write("### 音声テキスト変換結果:")
        st.write(g_result)
        summary = formatSummary(summarize(g_result))
        st.write("### テキスト要約結果:")
        st.write(summary, unsafe_allow_html=True)
