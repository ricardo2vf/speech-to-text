# speech-to-text
this is speech-to-text demo repo...

### prerequisite

1. you need Azure account for use speech-to-text api
2. you need openai account to user openai api key
3. install the neccesary pytho libaries..

```
$ pip install azure-cognitiveservices-speech
$ pip install openai
$ pip install streamlit
```

## How to launch app

1. Edit your local machine's ~/.bashrc. Add the following Enviroment Variables

```shell
export SPEECH_KEY=<Your Azure Speech Key>
export SPEECH_REGION=<Your Azure Speech Region>
export OPENAI_API_KEY=<Your OpenAI API Key>
```
2. Apply it to your bash

`source ~/.bashrc`

3. Start app

`streamlit run app.py`

## How to use app

1. Convert mp3 into wav with the mp3 file inside voice_data/mp3/
2. Convert wav data into text data, and summarize the text data
