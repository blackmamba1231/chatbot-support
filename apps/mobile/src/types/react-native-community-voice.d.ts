declare module '@react-native-community/voice' {
  export interface VoiceEvent {
    value?: string[];
    error?: string;
  }

  export interface Voice {
    onSpeechStart: (event: any) => void;
    onSpeechEnd: (event: any) => void;
    onSpeechResults: (event: VoiceEvent) => void;
    onSpeechError: (event: VoiceEvent) => void;
    start: (locale?: string) => Promise<void>;
    stop: () => Promise<void>;
    destroy: () => Promise<void>;
    removeAllListeners: () => void;
  }

  const Voice: Voice;
  export default Voice;
}
