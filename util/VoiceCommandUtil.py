import logging
import os
import queue
import re
import threading
import wave
import sys
import pyaudio

import config
if config.qtLibrary == "pyside6":
    from PySide6 import QtCore
    from PySide6.QtCore import QThread, QObject
else:
    from qtpy.PySide import QtCore
    from qtpy.QtCore import QThread

if __name__ == "__main__":
    config.noQt = False
from util.TextCommandParser import TextCommandParser
from db.BiblesSqlite import BiblesSqlite
import atexit

# Speech-to-text utility
# Uses Google cloud speech: https://pypi.org/project/google-cloud-speech/
#
# Examples:
# https://cloud.google.com/speech-to-text/docs/samples/speech-transcribe-streaming-mic
# https://github.com/googleapis/python-speech/blob/HEAD/samples/microphone/transcribe_streaming_mic.py
#
# Notes:
# https://cloud.google.com/speech-to-text/docs/streaming-recognize
#
# Setup Mac:
# brew install portaudio
#
# Setup Ubuntu:
# sudo apt install pulseaudio-equalizer
# sudo apt install jackd2
# sudo apt install multimedia-jack
#
# Setup:
# https://cloud.google.com/speech-to-text/docs/before-you-begin
# Create service account key google-cloud-key.json from:
# https://cloud.google.com/iam/docs/creating-managing-service-accounts
# https://console.cloud.google.com/apis/credentials
# pip install google-cloud-speech
# pip install wheel
# pip install pyaudio
# pip install numpy
class VoiceCommandUtil:

    commandReplacement = {"underscore": "_", "dash": "-", "colon": ":", "verse": ":"}

    RATE = 16000
    CHUNK = int(RATE / 10)  # 100ms

    def __init__(self, parent=None, language="en-US"):
        from google.oauth2 import service_account
        self.logger = logging.getLogger('uba')
        self.credentials = None
        self.parent = parent
        keyFile = 'google-cloud-key.json'
        if not os.path.exists(keyFile):
            raise Exception(f"{keyFile} does not exist")
        self.credentials = service_account.Credentials.from_service_account_file(keyFile)
        self.language_code = language
        self.speechTextCommand = []
        self.speechPartialCommand = ""
        self.runCommand = False
        textCommandParser = TextCommandParser(self)
        self.ubaTextCommands = [key for key in textCommandParser.interpreters.keys()]
        bibles = BiblesSqlite().getFormattedBibleList()
        self.bibleMap = {}
        for bible in bibles:
            self.bibleMap[bible.lower()] = bible
        self.frames = []

    def buildTextCommand(self, phrase):
        for search in self.wordReplacement.keys():
            phrase = re.sub(search, self.wordReplacement[search], phrase)
        phrase = self.replaceBibles(phrase)
        cmd = phrase.lower()
        if cmd in ["clear", "reset"]:
            self.speechTextCommand = []
            self.speechPartialCommand = ""
        elif cmd in ["delete"]:
            if len(self.speechTextCommand) > 0 and len(self.speechPartialCommand) == 0:
                self.speechTextCommand.pop()
            self.speechPartialCommand = ""
        elif len(self.speechTextCommand) == 0:
            word = phrase.replace(" ", "").lower()
            if word in self.ubaTextCommands:
                self.speechTextCommand.append(word)
                self.speechPartialCommand = ""
            elif "_" + word in self.ubaTextCommands:
                self.speechTextCommand.append("_" + word)
                self.speechPartialCommand = ""
            else:
                self.speechPartialCommand = phrase
        else:
            if cmd in ["separator"]:
                self.speechTextCommand.append(self.speechPartialCommand)
                self.speechPartialCommand = ""
            else:
                if len(self.speechPartialCommand) > 0:
                    self.speechPartialCommand += " "
                self.speechPartialCommand += phrase
        if self.parent is None:
            print("> " + self.getCommandString(True))
        else:
            self.parent.textCommandLineEdit.setText(self.getCommandString(True))

    def replaceBibles(self, phrase):
        words = phrase.split(" ")
        newPhrase = []
        for word in words:
            if word.lower() in self.bibleMap.keys():
                newPhrase.append(self.bibleMap[word.lower()])
            else:
                newPhrase.append(word)
        return " ".join(newPhrase)

    # This works in standalone mode for dev purposes, but will not work in GUI
    def transcribeFromMicrophoneUsingMicrophoneStream(self):
        from google.cloud import speech

        if not self.credentials:
            return

        client = speech.SpeechClient(credentials=self.credentials)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.RATE,
            language_code=self.language_code,
        )

        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True,
            single_utterance=False
        )
        with MicrophoneStream(self.RATE, self.CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )

            responses = client.streaming_recognize(streaming_config, requests)
            self.listenLoop(responses)

        if self.runCommand:
            if self.parent is None:
                print(self.getCommandString())
            else:
                self.parent.runTextCommand(self.getCommandString())

    def listenLoop(self, responses):
        """Iterates through server responses and prints them.

        The responses passed is a generator that will block until a response
        is provided by the server.

        Each response may contain multiple results, and each result may contain
        multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
        print only the transcription for the top alternative of the top result.

        In this case, responses are provided for interim results as well. If the
        response is an interim one, print a line feed at the end of it, to allow
        the next result to overwrite it, until the response is a final one. For the
        final one, print a newline to preserve the finalized transcription.
        """
        num_chars_printed = 0
        for response in responses:
            if not response.results:
                continue

            # The `results` list is consecutive. For streaming, we only care about
            # the first result being considered, since once it's `is_final`, it
            # moves on to considering the next utterance.
            result = response.results[0]
            if not result.alternatives:
                continue

            # Display the transcription of the top alternative.
            transcript = result.alternatives[0].transcript

            # Display interim results, but with a carriage return at the end of the
            # line, so subsequent lines will overwrite them.
            #
            # If the previous result was longer than this one, we need to print
            # some extra spaces to overwrite the previous result
            overwrite_chars = " " * (num_chars_printed - len(transcript))

            if not result.is_final:
                if self.parent is None:
                    sys.stdout.write(transcript + overwrite_chars + "\r")
                    sys.stdout.flush()
                    num_chars_printed = len(transcript)
                else:
                    self.parent.textCommandLineEdit.setText(transcript)
            else:
                # if re.search(r"\b(exit|quit|enter|return)\b", transcript, re.I):
                #     break
                transcript = transcript.strip()
                if transcript.lower() in ["exit", "quit", "cancel"]:
                    break
                elif transcript.lower() in ["enter", "return", "go", "execute"]:
                    self.runCommand = True
                    break
                self.buildTextCommand(transcript)

                num_chars_printed = 0

    def buildTextCommand(self, phrase):
        cmd = phrase.lower()
        if cmd in ["clear"]:
            self.speechTextCommand = []
            self.speechPartialCommand = ""
        elif cmd in ["delete"]:
            if len(self.speechTextCommand) > 0 and len(self.speechPartialCommand) == 0:
                self.speechTextCommand.pop()
            self.speechPartialCommand = ""
        elif cmd in self.commandReplacement.keys():
            self.speechPartialCommand.append(self.commandReplacement[cmd])
        elif len(self.speechTextCommand) == 0:
            word = phrase.replace(" ", "").lower()
            if word in self.ubaTextCommands:
                self.speechTextCommand.append(word)
                self.speechPartialCommand = ""
            elif "_" + word in self.ubaTextCommands:
                self.speechTextCommand.append("_" + word)
                self.speechPartialCommand = ""
            else:
                self.speechPartialCommand = phrase
        else:
            if cmd in ["separator", "colons", "colon's"]:
                self.speechTextCommand.append(self.speechPartialCommand)
                self.speechPartialCommand = ""
            else:
                if len(self.speechPartialCommand) > 0:
                    self.speechPartialCommand += " "
                self.speechPartialCommand += phrase
        print("> " + self.getCommandString(True))


    def getCommandString(self, building=False):
        if len(self.speechTextCommand) == 0:
            return self.speechPartialCommand
        elif len(self.speechTextCommand) == 1:
            if building or len(self.speechPartialCommand) > 0:
                return self.speechTextCommand[0] + ":::" + self.speechPartialCommand
            else:
                self.speechTextCommand[0]
        else:
            return ":::".join(self.speechTextCommand) + ":::" + self.speechPartialCommand

    def transcribeFile(self, speechFile):
        from google.cloud import speech
        import io

        client = speech.SpeechClient(credentials=self.credentials)

        with io.open(speechFile, "rb") as audio_file:
            content = audio_file.read()

        frame_rate, channels = self.frameRateChannel(speechFile)

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code="en-US",
            sample_rate_hertz=frame_rate,
            audio_channel_count=channels,
        )

        response = client.recognize(config=config, audio=audio)

        for result in response.results:
            print(u"Transcript: {}".format(result.alternatives[0].transcript))

    def frameRateChannel(self, audio_file_name):
        with wave.open(audio_file_name, "rb") as wave_file:
            frame_rate = wave_file.getframerate()
            channels = wave_file.getnchannels()
            return frame_rate, channels


# GUI mode transcription
class TranscribeFromMicrophone(QObject):
    def start(self):
        from google.cloud import speech

        from google.oauth2 import service_account
        self.logger = logging.getLogger('uba')
        self.credentials = None
        keyFile = 'google-cloud-key.json'
        if not os.path.exists(keyFile):
            raise Exception(f"{keyFile} does not exist")
        self.credentials = service_account.Credentials.from_service_account_file(keyFile)

        self.mic = MicrophoneRecorder()
        self.mic.start()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.handleNewData)
        self.timer.start(50)
        self.frames = []
        self.count = 0
        self.client = speech.SpeechClient(credentials=self.credentials)

    def stop(self):
        self.timer.stop()
        self.finished.emit()

    def handleNewData(self):
        from google.cloud import speech

        data = self.mic.get_frames()
        self.count = self.count + 1
        if self.count > 20 * 3:
            print(".")
            print(data)
            byteData = bytes(data)
            audio = speech.RecognitionAudio(content=byteData)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                language_code="en-US",
                sample_rate_hertz=VoiceCommandUtil.RATE
            )

            response = self.client.recognize(config=config, audio=audio)

            for result in response.results:
                print(u"Transcript: {}".format(result.alternatives[0].transcript))


# https://flothesof.github.io/pyqt-microphone-fft-application.html
class MicrophoneRecorder:
    RATE = 16000
    CHUNK = int(RATE / 10)  # 100ms

    def __init__(self):
        self.rate = self.RATE
        self.chunksize = self.CHUNK
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.chunksize,
                                  stream_callback=self.new_frame)
        self.lock = threading.Lock()
        self.stop = False
        self.frames = bytearray()
        atexit.register(self.close)

    def new_frame(self, data, frame_count, time_info, status):
        import numpy as np
        data = np.frombuffer(data, 'int16')
        with self.lock:
            self.frames.extend(data)
            if self.stop:
                return None, pyaudio.paComplete
        return None, pyaudio.paContinue

    def get_frames(self):
        with self.lock:
            frames = self.frames
            self.frames = bytearray()
            return frames

    def start(self):
        self.stream.start_stream()

    def close(self):
        with self.lock:
            self.stop = True
        self.stream.close()
        self.p.terminate()

# Command line transcription
class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    print("Start")

    VoiceCommandUtil().transcribeFromMicrophoneUsingMicrophoneStream()

    # thread = QThread()
    # transcribe = TranscribeFromMicrophone()
    # transcribe.moveToThread(thread)
    # thread.started.connect(transcribe.start)
    # thread.start()
    # app = QApplication(sys.argv)
    # app.exec()

    # VoiceCommandUtil().transcribeFile("temp/harvard.wav")
    print("End")