'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, CheckCircle, Info } from 'lucide-react';
import { GenerateResponse } from '@/app/lib/api';

interface Message {
  id: string;
  type: 'user' | 'agent' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    duration?: number;
    iterations?: number;
    extracted_locators?: number;
    saved_files?: string[];
  };
}

interface AgentChatProps {
  onGenerate: (prompt: string) => Promise<GenerateResponse>;
  isGenerating: boolean;
}

export default function AgentChat({ onGenerate, isGenerating }: AgentChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'system',
      content: 'Welcome! I can generate Playwright Page Object Models from live websites.\n\nTry:\n• "Generate POM for https://example.com"\n• "Navigate to https://google.com and create a POM"',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || isGenerating) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const prompt = input;
    setInput('');

    try {
      const response = await onGenerate(prompt);

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: response.response || 'Code generated successfully!',
        timestamp: new Date(),
        metadata: {
          duration: response.duration,
          iterations: response.iterations,
          extracted_locators: Object.keys(response.extracted_locators || {}).length,
          saved_files: response.saved_files,
        },
      };

      setMessages((prev) => [...prev, agentMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: `❌ Error: ${error.message || 'Failed to generate code'}`,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 border border-gray-700 rounded-lg">
      {/* Chat Header */}
      <div className="px-4 py-3 bg-gray-800 border-b border-gray-700">
        <h2 className="text-lg font-semibold text-white">Agent Chat</h2>
        <p className="text-sm text-gray-400">Playwright POM Generator</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : message.type === 'system'
                  ? 'bg-gray-800 text-gray-300 border border-gray-700'
                  : 'bg-gray-800 text-white'
              }`}
            >
              {/* Message Content */}
              <div className="text-sm whitespace-pre-wrap break-words">{message.content}</div>

              {/* Metadata */}
              {message.metadata && (
                <div className="mt-2 pt-2 border-t border-gray-700 text-xs text-gray-400 space-y-1">
                  {message.metadata.duration && (
                    <div className="flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" />
                      <span>Duration: {message.metadata.duration.toFixed(2)}s</span>
                    </div>
                  )}
                  {message.metadata.iterations && (
                    <div className="flex items-center gap-1">
                      <Info className="w-3 h-3" />
                      <span>Iterations: {message.metadata.iterations}</span>
                    </div>
                  )}
                  {message.metadata.extracted_locators !== undefined && (
                    <div className="flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" />
                      <span>Locators: {message.metadata.extracted_locators}</span>
                    </div>
                  )}
                  {message.metadata.saved_files && message.metadata.saved_files.length > 0 && (
                    <div className="mt-1">
                      <div className="font-medium text-gray-300">Files saved:</div>
                      {message.metadata.saved_files.map((file) => (
                        <div key={file} className="ml-2 text-green-400 truncate">
                          ✓ {file}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Timestamp */}
              <div className="mt-1 text-xs text-gray-500">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {isGenerating && (
          <div className="flex justify-start">
            <div className="bg-gray-800 rounded-lg p-3 flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
              <span className="text-sm text-gray-300">Agent is working...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-700 bg-gray-800">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Type your prompt here..."
            disabled={isGenerating}
            className="flex-1 bg-gray-900 text-white border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500 disabled:opacity-50"
          />
          <button
            onClick={handleSendMessage}
            disabled={isGenerating || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg px-4 py-2 flex items-center gap-2 transition-colors"
          >
            {isGenerating ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            Generate
          </button>
        </div>
      </div>
    </div>
  );
}