import React, { useState, useRef } from 'react';
import './ChatWidget.css';

function VoiceInput({ onSendMessage, disabled }) {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const silenceTimerRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const sourceRef = useRef(null);
  const streamRef = useRef(null);

  const startRecording = async () => {
    if (disabled) return;
  
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
    } catch (err) {
      console.error("User denied microphone or no access", err);
      alert("Microphone access denied or not available. Please allow microphone access and try again.");
      return;
    }
  
    try {
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
  
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
  
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
  
      mediaRecorder.onstop = () => {
        const totalSize = audioChunksRef.current.reduce((sum, chunk) => sum + chunk.size, 0);
        if (totalSize < 1024) {
          console.log("Discarded empty/silent recording.");
        } else {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          onSendMessage(audioBlob);
        }
  
        clearInterval(silenceTimerRef.current);
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
        }
        if (audioContextRef.current) {
          audioContextRef.current.close();
        }
      };
  
      mediaRecorder.start();
      setIsRecording(true);
      monitorSilence(stream);
    } catch (err) {
      console.error("Recording setup failed:", err);
    }
  };
  
  

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // 🔊 Monitor silence and auto-stop after 5s of silence
  const monitorSilence = (stream) => {
    const audioContext = new AudioContext();
    audioContextRef.current = audioContext;
  
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 512;
    analyserRef.current = analyser;
  
    const source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);
    sourceRef.current = source;
  
    const dataArray = new Uint8Array(analyser.fftSize);
    const rmsBuffer = [];
    const RMS_BUFFER_SIZE = 10;  // Number of recent RMS values to average
    const SILENCE_THRESHOLD = 0.02; // Adjust this value (0.02 ~ low volume)
    const SILENCE_DURATION = 5000; // 5 seconds
  
    let silenceStart = null;
  
    silenceTimerRef.current = setInterval(() => {
      analyser.getByteTimeDomainData(dataArray);
  
      // Calculate RMS (Root Mean Square)
      let sumSquares = 0;
      for (let i = 0; i < dataArray.length; i++) {
        const normalized = (dataArray[i] - 128) / 128; // normalize between -1 and 1
        sumSquares += normalized * normalized;
      }
      const rms = Math.sqrt(sumSquares / dataArray.length);
  
      // Push rms into buffer
      rmsBuffer.push(rms);
      if (rmsBuffer.length > RMS_BUFFER_SIZE) {
        rmsBuffer.shift();
      }
  
      // Calculate average RMS from buffer
      const avgRms = rmsBuffer.reduce((a, b) => a + b, 0) / rmsBuffer.length;
  
      // Check if below threshold (silence)
      if (avgRms < SILENCE_THRESHOLD) {
        if (silenceStart === null) {
          silenceStart = Date.now();
        } else if (Date.now() - silenceStart >= SILENCE_DURATION) {
          stopRecording(); // stop after 5 seconds of silence
        }
      } else {
        silenceStart = null; // reset timer if sound detected
      }
    }, 200); // check every 200ms
  };
  

  return (
    <button
      className={`vogo-chat-voice-button ${isRecording ? 'vogo-chat-voice-recording' : ''}`}
      onClick={isRecording ? stopRecording : startRecording}
      disabled={disabled}
      aria-label={isRecording ? 'Stop recording' : 'Start voice recording'}
      title={isRecording ? 'Stop recording' : 'Hold to record voice message'}
    >
      <span role="img" aria-hidden="true">
        {isRecording ? '⬛' : '🎤'}
      </span>
    </button>
  );
}

export default VoiceInput;
