import React, { useState, useRef } from 'react';
import './ChatWidget.css';

function VoiceInput({ onVoiceRecorded, disabled }) {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    if (disabled) return;
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/mp3' });
        onVoiceRecorded(audioBlob);
        
        // Stop all tracks in the stream
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Failed to access microphone. Please make sure microphone permissions are granted and try again.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
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
