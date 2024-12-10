import React, { useState, useRef } from 'react';
import { IconButton, CircularProgress } from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';
import { audioService } from '../services/audioService';
import clsx from 'clsx';

interface AudioRecorderProps {
  onTranscriptionComplete: (text: string) => void;
}

const AudioRecorder: React.FC<AudioRecorderProps> = ({ onTranscriptionComplete }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true
        } 
      });
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm;codecs=opus' });
        await sendAudioToServer(audioBlob);
      };

      mediaRecorder.start(1000); // Grabar en chunks de 1 segundo
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Error al acceder al micrófono. Por favor, asegúrate de dar permisos de audio.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
      setIsProcessing(true);
    }
  };

  const sendAudioToServer = async (audioBlob: Blob) => {
    try {
      const transcribedText = await audioService.transcribeAudio(audioBlob);
      onTranscriptionComplete(transcribedText);
    } catch (error) {
      alert('Error al procesar el audio: ' + (error instanceof Error ? error.message : 'Error desconocido'));
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <IconButton 
      onClick={isRecording ? stopRecording : startRecording}
      disabled={isProcessing}
      className={clsx('audio-recorder-button', { recording: isRecording })}
    >
      {isProcessing ? (
        <CircularProgress size={24} />
      ) : isRecording ? (
        <StopIcon className="stop-icon" />
      ) : (
        <MicIcon />
      )}
    </IconButton>
  );
};

export default AudioRecorder; 