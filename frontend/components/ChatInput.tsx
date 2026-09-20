"use client";

import { useCallback, useRef, useState } from "react";

interface Props {
  onSend: (text: string) => void;
  onUploadClick: () => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function ChatInput({
  onSend,
  onUploadClick,
  disabled = false,
  placeholder = "Ask about patents, trademarks, copyright, or AYUSH regulations…",
}: Props) {
  const [value, setValue] = useState("");
  const [isListening, setIsListening] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const recognitionRef = useRef<any>(null);

  const handleSend = useCallback(() => {
    const text = value.trim();
    if (!text || disabled) return;
    onSend(text);
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [value, disabled, onSend]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
    // Auto-resize
    const ta = e.target;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 200)}px`;
  };

  const toggleVoice = useCallback(() => {
    const win = typeof window !== "undefined" ? (window as any) : {};
    const SpeechRecognitionClass = win.SpeechRecognition || win.webkitSpeechRecognition;
    if (!SpeechRecognitionClass) {
      alert("Voice input is not supported in this browser. Please use Chrome.");
      return;
    }

    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      return;
    }

    const recognition: any = new SpeechRecognitionClass();
    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setValue((prev) => (prev ? `${prev} ${transcript}` : transcript));
      setIsListening(false);
    };

    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);

    recognitionRef.current = recognition;
    recognition.start();
    setIsListening(true);
  }, [isListening]);

  const canSend = value.trim().length > 0 && !disabled;

  return (
    <div className="relative rounded-2xl border border-slate-700/80 bg-slate-900/80 backdrop-blur-sm shadow-2xl focus-within:border-indigo-500/60 focus-within:shadow-indigo-500/10 transition-all duration-300">
      {/* Textarea */}
      <textarea
        ref={textareaRef}
        id="chat-input"
        rows={1}
        value={value}
        onChange={handleTextareaChange}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder={placeholder}
        aria-label="Chat input"
        className="w-full resize-none bg-transparent text-slate-100 placeholder-slate-500 text-sm px-5 py-4 pr-36 focus:outline-none disabled:opacity-50"
        style={{ minHeight: "56px", maxHeight: "200px" }}
      />

      {/* Action buttons */}
      <div className="absolute right-2 bottom-2 flex items-center gap-1.5">
        {/* Upload */}
        <button
          type="button"
          id="upload-pdf-btn"
          onClick={onUploadClick}
          disabled={disabled}
          className="w-9 h-9 rounded-xl flex items-center justify-center text-slate-400 hover:text-slate-200 hover:bg-slate-700 transition-all disabled:opacity-40"
          title="Upload PDF"
          aria-label="Upload a PDF document"
        >
          📎
        </button>

        {/* Mic */}
        <button
          type="button"
          id="voice-input-btn"
          onClick={toggleVoice}
          disabled={disabled}
          className={`w-9 h-9 rounded-xl flex items-center justify-center transition-all disabled:opacity-40
            ${isListening
              ? "text-rose-400 bg-rose-500/20 animate-pulse"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-700"
            }`}
          title={isListening ? "Stop listening" : "Voice input"}
          aria-label={isListening ? "Stop voice input" : "Start voice input"}
        >
          🎤
        </button>

        {/* Send */}
        <button
          type="button"
          id="send-message-btn"
          onClick={handleSend}
          disabled={!canSend}
          className={`w-9 h-9 rounded-xl flex items-center justify-center font-bold text-sm transition-all duration-200
            ${canSend
              ? "bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/30"
              : "bg-slate-800 text-slate-600 cursor-not-allowed"
            }`}
          aria-label="Send message"
        >
          ↑
        </button>
      </div>
    </div>
  );
}
