import json
import pyttsx3
import pyaudio
import vosk
import requests


def start():
    print('Welcome to Voice assistant v.0.2!')
    print('Usage:')
    print('Say "word <word>" to know its definition, spelling, etc.')
    print('After picking a word, use one of the commands below')
    print('Commands:')
    print('Define, Spelling, Example, Link, Exit')


tts = pyttsx3.init('sapi5')
voices = tts.getProperty('voices')
print(voices)
tts.setProperty('voices', 'en')

for voice in voices:
    print(voice.name)
    if voice.name == 'Microsoft Zira Desktop - English (United States)':
        tts.setProperty('voice', voice.id)

model = vosk.Model('vosk-model-small-en-us-0.15')
record = vosk.KaldiRecognizer(model, 16000)
pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16,
                 channels=1,
                 rate=16000,
                 input=True,
                 frames_per_buffer=8000)
stream.start_stream()


def listen():

    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if record.AcceptWaveform(data) and len(data) > 0:
            answer = json.loads(record.Result())
            if answer['text']:
                yield answer['text']


def say(saying):

    tts.say(saying)
    tts.runAndWait()


def give_definition(word):

    try:
        response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
        data = response.json()
        definition = data[0]['meanings'][0]['definitions'][0]['definition']
        print(definition)
        say(definition)

    except Exception:
        print('Definition not found')


def give_spelling(word):

    try:
        response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
        data = response.json()
        spelling = data[0]['phonetic']
        print(spelling)
        say(word)

    except Exception:
        print('Spelling not found')

def save_word(word):

    response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
    data = response.json()
    definition = data[0]['meanings'][0]['definitions'][0]['definition']

    saved_info = f'{word} - {definition}'

    with open("saved.txt", "a") as f:
        f.write(saved_info)
        f.write('\n')
    f.close()

    say(f'Saved word {word}')
    print(f"Successfully saved the word {word}")


def give_example(word):

    try:
        response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
        data = response.json()
        example = data[0]['meanings'][0]['definitions'][0]['example']
        print(example)
        say(example)

    except Exception:
        print(f'Could not find example of {word}')


def give_link(word):

    try:
        response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
        data = response.json()
        urls = data[0]['sourceUrls'][0]
        print(urls)

    except Exception:
        print(f'Could not find link to the word {word}')


start()
for speech in listen():
    print('You:', speech)

    if 'word' in speech:
        words = speech.split()
        word = words[words.index('word')+1]

        try:
            response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
            data = response.json()

        except Exception as ex:
            print(ex)

        finally:
            print(f'Word: {word}')

    elif speech in ['meaning', 'definition', 'give meaning', 'give definition', 'define']:
        give_definition(word)

    elif speech in ['spell']:
        give_spelling(word)

    elif speech in ['example', 'give example', 'usage']:
        give_example(word)

    elif speech in ['link', 'source', 'give source']:
        give_link(word)

    elif speech in ['save', 'save word', 'download']:
        save_word(word)

    elif speech in ['bye', 'exit', 'quit', 'stop', 'break', 'goodbye']:
        break

    else:
        print('Sorry, I could not recognize your command')
