import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import {
  PaperAirplaneIcon,
  XMarkIcon,
  ChatBubbleBottomCenterTextIcon
} from '@heroicons/react/24/outline';
import { ChatBubbleLeftEllipsisIcon } from '@heroicons/react/24/solid';

const ContributorTwinChat = ({ contributor }) => {
  const [prompt, setPrompt] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingResponse, setStreamingResponse] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);
  const responseRef = useRef(null);

  useEffect(() => {
    if (responseRef.current) {
      responseRef.current.scrollTop = responseRef.current.scrollHeight;
    }
  }, [streamingResponse]);

  const handleInputFocus = () => {
    setIsFocused(true);
    if (!isExpanded && !isStreaming) {
      setIsExpanded(true);
    }
  };

  const handleInputBlur = () => {
    setIsFocused(false);
    if (isExpanded && !isStreaming && !streamingResponse) {
      setIsExpanded(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim() || isStreaming) return;

    setIsStreaming(true);
    setError(null);
    setStreamingResponse('');

    try {
      const response = await fetch('http://localhost:8000/api/twin_stream/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          prompt: prompt.trim(),
          contributor_id: contributor.id
        }),
      });
      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const text = decoder.decode(value, { stream: true });
        setStreamingResponse(prev => prev + text);
      }
    } catch (err) {
      console.error('Error streaming response:', err);
      setError(`Failed to get response: ${err.message}`);
    } finally {
      setIsStreaming(false);
    }
  };

  const resetChat = () => {
    setStreamingResponse('');
    setPrompt('');
    setIsStreaming(false);
    setError(null);
  };

  const closeExpanded = () => {
    if (!isStreaming) {
      setIsExpanded(false);
      setStreamingResponse('');
    }
  };

  // Chat toggle button when closed
  if (!isExpanded && !isFocused && !streamingResponse && !isStreaming) {
    return (
      <button 
        onClick={() => setIsExpanded(true)}
        className="fixed bottom-6 right-6 z-50 p-4 bg-indigo-600 text-white rounded-full shadow-lg hover:bg-indigo-700 hover:scale-105 transition-all flex items-center justify-center group"
      >
        <ChatBubbleBottomCenterTextIcon className="h-6 w-6" />
        <span className="max-w-0 overflow-hidden whitespace-nowrap group-hover:max-w-xs transition-all duration-300 ml-0 group-hover:ml-2">
          Chat with {contributor.username}'s Twin
        </span>
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-96 max-w-[calc(100vw-3rem)] z-50">
      <div
        className={`rounded-2xl bg-white dark:bg-slate-800 shadow-2xl border border-gray-200 dark:border-slate-700 overflow-hidden transition-all duration-300 ease-in-out`}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-indigo-800 p-4 flex justify-between items-center text-white">
          <div className="flex items-center space-x-3">
            <img src={contributor.avatar_url} alt={contributor.username} className="w-8 h-8 rounded-full border-2 border-white/30" />
            <div>
              <h3 className="font-semibold text-sm leading-tight">{contributor.username}</h3>
              <span className="text-[10px] text-indigo-100 uppercase tracking-wider font-semibold">Digital Twin (AI)</span>
            </div>
          </div>
          <button
            onClick={closeExpanded}
            className="text-white/70 hover:text-white p-1 rounded-full hover:bg-white dark:bg-slate-800/10 transition-colors"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        {/* Content Area */}
        <div
          className={`px-5 pt-5 pb-4 transition-all duration-300 ease-in-out ${
            streamingResponse || isStreaming ? 'h-[300px]' : 'h-[120px]'
          } overflow-y-auto bg-gray-50 dark:bg-slate-900/50`}
          ref={responseRef}
        >
          {!streamingResponse && !isStreaming && !error && (
            <div className="text-center mt-2">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                Ask me about my recent commits, design decisions, or the repositories I work on.
              </p>
              <div className="space-y-2">
                <button 
                  onClick={() => setPrompt("What was your most recent contribution about?")}
                  className="w-full text-left text-xs bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 p-2 rounded-lg hover:border-indigo-300 hover:text-indigo-600 transition-colors shadow-sm"
                >
                  "What was your most recent contribution about?"
                </button>
                <button 
                  onClick={() => setPrompt("Can you explain the main repository you work on?")}
                  className="w-full text-left text-xs bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 p-2 rounded-lg hover:border-indigo-300 hover:text-indigo-600 transition-colors shadow-sm"
                >
                  "Can you explain the main repository you work on?"
                </button>
              </div>
            </div>
          )}

          {/* Streaming Response */}
          {(streamingResponse || isStreaming) && (
            <div className="prose prose-sm max-w-none text-gray-800 dark:text-gray-100">
              <div className="markdown-content">
                <ReactMarkdown rehypePlugins={[rehypeRaw]}>
                  {streamingResponse}
                </ReactMarkdown>

                {isStreaming && (
                  <span className="typing-cursor inline-block ml-0.5 w-1.5 h-4 align-middle bg-indigo-600 animate-pulse"></span>
                )}
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 p-3 rounded-md border border-red-100">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}
        </div>

        {/* Input Area */}
        <form onSubmit={handleSubmit} className="p-3 bg-white dark:bg-slate-800 border-t border-gray-100 dark:border-slate-700">
          <div className="flex items-center">
            <div className="relative flex-grow">
              <input
                ref={inputRef}
                type="text"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onFocus={handleInputFocus}
                onBlur={handleInputBlur}
                placeholder={`Message ${contributor.username}...`}
                className={`w-full py-2.5 pl-4 pr-12 rounded-full border ${
                  isFocused ? 'border-indigo-500 ring-2 ring-indigo-100' : 'border-gray-200 dark:border-slate-700 bg-gray-50 dark:bg-slate-900/50'
                } focus:outline-none focus:bg-white dark:bg-slate-800 text-sm transition-all`}
                disabled={isStreaming}
              />
              <button
                type="submit"
                disabled={!prompt.trim() || isStreaming}
                className={`absolute right-1 top-1 bottom-1 p-2 rounded-full ${
                  prompt.trim() && !isStreaming
                    ? 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-200'
                    : 'bg-gray-100 dark:bg-slate-700 text-gray-400 cursor-not-allowed'
                } transition-all flex items-center justify-center`}
              >
                <PaperAirplaneIcon className="h-4 w-4 transform -rotate-45 ml-0.5" />
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ContributorTwinChat;
