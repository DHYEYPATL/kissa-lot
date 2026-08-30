"use client";

import React, { useState } from "react";
import { VoicePoweredOrb } from "@/components/ui/voice-powered-orb";
import { Button } from "@/components/ui/button";
import { Mic, MicOff } from "lucide-react";

export default function VoicePoweredOrbDemo() {
  const [isRecording, setIsRecording] = useState(false);
  const [voiceDetected, setVoiceDetected] = useState(false);

  const toggleRecording = () => {
    setIsRecording(!isRecording);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-8">
      <div className="flex flex-col items-center space-y-8 max-w-lg w-full">
        {/* Visual Orb Container */}
        <div className="w-80 h-80 md:w-96 md:h-96 relative rounded-2xl overflow-hidden shadow-2xl border border-white/10 bg-black/40 backdrop-blur-md">
          <VoicePoweredOrb
            enableVoiceControl={isRecording}
            className="w-full h-full"
            onVoiceDetected={setVoiceDetected}
          />
        </div>

        {/* Status Indicator */}
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span
            className={`inline-block w-2.5 h-2.5 rounded-full ${
              voiceDetected
                ? "bg-emerald-400 animate-pulse"
                : isRecording
                ? "bg-amber-400"
                : "bg-zinc-600"
            }`}
          />
          <span>
            {voiceDetected
              ? "Voice Detected (Active Modulation)"
              : isRecording
              ? "Listening for voice..."
              : "Microphone Inactive"}
          </span>
        </div>

        {/* Control Button */}
        <Button
          onClick={toggleRecording}
          variant={isRecording ? "destructive" : "default"}
          size="lg"
          className="px-8 py-3 font-semibold rounded-full shadow-lg"
        >
          {isRecording ? (
            <>
              <MicOff className="w-5 h-5 mr-3" />
              Stop Recording
            </>
          ) : (
            <>
              <Mic className="w-5 h-5 mr-3" />
              Start Voice Control
            </>
          )}
        </Button>

        {/* Instructions */}
        <p className="text-zinc-400 text-center text-sm">
          Click the button to enable voice control. Speak into your microphone to modulate the orb's rotation and surface dynamics in real time.
        </p>
      </div>
    </div>
  );
}
