"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import type { Session } from "@/types/session"
import "./query-panel.css"
import { secureFetch } from "@/utils/encryption"
import ChatHistorySidebar from "./chat-history-sidebar"
import ResultsDisplay from "./results-display"
import { API_BASE_URL } from "@/config/api"

// --- Helper Icons ---
const DatabaseIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 6C16.4183 6 20 7.34315 20 9C20 10.6569 16.4183 12 12 12C7.58172 12 4 10.6569 4 9C4 7.34315 7.58172 6 12 6Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M12 12C16.4183 12 20 13.3431 20 15C20 16.6569 16.4183 18 12 18C7.58172 18 4 16.6569 4 15C4 13.3431 7.58172 12 12 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M20 9V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M4 9V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
);

const UserIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M12 11C14.2091 11 16 9.20914 16 7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7C8 9.20914 9.79086 11 12 11Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
);

const MicIcon = () => (
 <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M19 10v2a7 7 0 0 1-14 0v-2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M12 19v4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M8 23h8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
);

const SummarizeIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M14 2v6h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M16 13H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M16 17H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M10 9H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
);
// --- End Helper Icons ---

const SpeechRecognition = typeof window !== 'undefined' && ((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition);
let recognition: any = null;
if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = 'en-US';
}

interface QueryPanelProps {
  session: Session
}

interface ChatMessage {
  id: number
  sender: "user" | "conversql"
  text: string
  results?: any[]
  error?: string
  timestamp: string;
}

export interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
}

export default function QueryPanel({ session }: QueryPanelProps) {
  const [query, setQuery] = useState("");
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const summarizeFileInputRef = useRef<HTMLInputElement>(null);
  const speechTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const storageKey = `conversql_history_${session.username}`;

  useEffect(() => {
    const saved = localStorage.getItem(storageKey);
    if (saved) {
      const parsed = JSON.parse(saved);
      setConversations(parsed);
      if (parsed.length > 0) setActiveConversationId(parsed[0].id);
    }
  }, [storageKey]);

  useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem(storageKey, JSON.stringify(conversations));
    } else {
      localStorage.removeItem(storageKey);
    }
  }, [conversations, storageKey]);

  useEffect(() => {
    chatContainerRef.current?.scrollTo({ top: chatContainerRef.current.scrollHeight, behavior: 'smooth' });
  }, [activeConversationId, conversations]);

  const activeConversation = conversations.find(c => c.id === activeConversationId);

  const handleNewChat = () => {
    const newConversation: Conversation = {
      id: `chat_${Date.now()}`,
      title: "New Query Session",
      messages: [{
        id: Date.now(),
        sender: "conversql",
        text: `Hello ${session.username}! How can I assist you with your query?`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]
    };
    setConversations([newConversation, ...conversations]);
    setActiveConversationId(newConversation.id);
  };

  const handleDeleteChat = (idToDelete: string) => {
    const updated = conversations.filter(conv => conv.id !== idToDelete);
    setConversations(updated);
    if (activeConversationId === idToDelete) {
      setActiveConversationId(updated.length > 0 ? updated[0].id : null);
    }
  };

  const updateConversation = (updatedMessages: ChatMessage[]) => {
    const updated = conversations.map(conv => {
      if (conv.id === activeConversationId) {
        const isNew = conv.title === "New Query Session" && conv.messages.length === 1;
        const userMsg = updatedMessages.find(m => m.sender === 'user');
        const newTitle = isNew && userMsg ? userMsg.text.substring(0, 30) + '...' : conv.title;
        return { ...conv, title: newTitle, messages: updatedMessages };
      }
      return conv;
    });
    setConversations(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeConversationId) {
      handleNewChat();
      setTimeout(() => handleSubmit(e), 50);
      return;
    }

    const userQuery = query.trim();
    if (!userQuery) return;

    setQuery("");

    const newUserMessage: ChatMessage = {
      id: Date.now(),
      sender: "user",
      text: userQuery,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    const currentMessages = activeConversation ? [...activeConversation.messages, newUserMessage] : [newUserMessage];
    updateConversation(currentMessages);
    setIsLoading(true);

    try {
      const payload = {
        username: session.username,
        password: session.password,
        query: userQuery,
      };
      const data = await secureFetch("/query", payload);
      const newAssistantMessage: ChatMessage = {
        id: Date.now() + 1,
        sender: "conversql",
        text: data.commentary || data.detail || "Sorry, I ran into an issue.",
        results: data.sample_rows || [],
        error: data.error || (data.detail && !data.commentary ? data.detail : undefined),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      updateConversation([...currentMessages, newAssistantMessage]);

    } catch (err) {
      const errorAssistantMessage: ChatMessage = {
        id: Date.now() + 1,
        sender: "conversql",
        text: "A connection or encryption error occurred.",
        error: (err as Error).message,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      updateConversation([...currentMessages, errorAssistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSummarizeClick = () => {
    summarizeFileInputRef.current?.click();
  };

  const handleSummarizeFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !activeConversation) return;

    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    
    const summarizingMessage: ChatMessage = {
        id: Date.now(),
        sender: "conversql",
        text: `Summarizing ${file.name}...`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    updateConversation([...activeConversation.messages, summarizingMessage]);

    try {
      const response = await fetch(`${API_BASE_URL}/summarize-document`, {
        method: 'POST',
        body: formData,
      });

      let currentMessages = [...activeConversation.messages];
      currentMessages = currentMessages.filter(m => m.id !== summarizingMessage.id);

      if (response.ok) {
        const data = await response.json();
        const summaryMessage: ChatMessage = {
            id: Date.now() + 1,
            sender: "conversql",
            text: data.summary,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        updateConversation([...currentMessages, summaryMessage]);

      } else {
        const errorData = await response.json();
        const errorMessage: ChatMessage = {
          id: Date.now() + 1,
          sender: "conversql",
          text: `Failed to summarize document.`,
          error: errorData.detail || 'Unknown error',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        updateConversation([...currentMessages, errorMessage]);
      }
    } catch (error) {
      let currentMessages = [...activeConversation.messages].filter(m => m.id !== summarizingMessage.id);
      const errorMessage: ChatMessage = {
        id: Date.now() + 1,
        sender: "conversql",
        text: `An error occurred during document summarization.`,
        error: (error as Error).message,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      updateConversation([...currentMessages, errorMessage]);
    } finally {
      setIsLoading(false);
      if(summarizeFileInputRef.current) summarizeFileInputRef.current.value = "";
    }
  };

  const stopListeningAndSubmit = () => {
    if (recognition && isListening) {
      recognition.stop();
      setIsListening(false);
      // Use a timeout to ensure the final query state is set before submitting
      setTimeout(() => {
        const form = document.getElementById("query-form");
        if (form) {
            form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
        }
      }, 100);
    }
  };

  useEffect(() => {
    if (!recognition) return;

    recognition.onresult = (event: any) => {
      if (speechTimeoutRef.current) clearTimeout(speechTimeoutRef.current);

      let finalTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        }
      }

      if (finalTranscript) {
        setQuery(prev => (prev + finalTranscript.trim() + ' ').trim());
      }

      speechTimeoutRef.current = setTimeout(() => {
        stopListeningAndSubmit();
      }, 1500);
    };

    recognition.onerror = (event: any) => {
      console.error("Speech recognition error", event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      if (speechTimeoutRef.current) clearTimeout(speechTimeoutRef.current);
      setIsListening(false);
    };

    return () => {
      recognition.stop();
      if (speechTimeoutRef.current) clearTimeout(speechTimeoutRef.current);
    };
  }, [isListening]);

  const handleVoiceListen = () => {
    if (!recognition) {
        alert("Sorry, your browser doesn't support speech recognition.");
        return;
    }
    if (isListening) {
      recognition.stop(); // Manually stop listening
    } else {
      setQuery("");
      recognition.start();
      setIsListening(true);
    }
  };

  return (
    <div className="query-panel-layout">
      <ChatHistorySidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onNewChat={handleNewChat}
        onSelectChat={setActiveConversationId}
        onDeleteChat={handleDeleteChat}
      />
      <div className="query-panel">
        <div className="chat-container" ref={chatContainerRef}>
          {activeConversation ? activeConversation.messages.map((msg) => (
            <div key={msg.id} className={`chat-message-wrapper ${msg.sender}`}>
              <div className="avatar-wrapper">
                {msg.sender === 'conversql' ? <DatabaseIcon /> : <UserIcon />}
              </div>
              <div className="message-content">
                <div className="message-bubble">
                  <p className="message-text">{msg.text}</p>
                  <ResultsDisplay results={msg.results} />
                  {msg.error && (
                    <div className="message-error">
                      <h4>Error Details:</h4>
                      <p>{msg.error}</p>
                    </div>
                  )}
                </div>
                <div className="message-timestamp">{msg.timestamp}</div>
              </div>
            </div>
          )) : (
            <div className="no-chat-selected">
              <h2>Welcome to ConversQL</h2>
              <p>Select a query session from the sidebar or start a new one.</p>
              <button onClick={handleNewChat}>Start New Query</button>
            </div>
          )}
          {isLoading && (
            <div className="chat-message-wrapper conversql">
               <div className="avatar-wrapper"><DatabaseIcon /></div>
              <div className="message-content">
                <div className="message-bubble">
                  <div className="typing-indicator"><span></span><span></span><span></span></div>
                </div>
              </div>
            </div>
          )}
        </div>

        <form id="query-form" onSubmit={handleSubmit} className="query-input-form">
          <input type="file" ref={summarizeFileInputRef} style={{ display: 'none' }} onChange={handleSummarizeFileChange} accept=".txt,.csv,.md" />
          
          <button type="button" className="attachment-button" onClick={handleSummarizeClick} title="Summarize Document">
            <SummarizeIcon />
          </button>

          <div className="textarea-wrapper">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={isListening ? "Listening... stop talking to send." : (isLoading ? "Processing..." : "Ask a question or click the mic to talk...")}
              rows={1}
              disabled={isLoading || !activeConversationId}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />
            {recognition && (
                <button type="button" className={`mic-button ${isListening ? 'listening' : ''}`} onClick={handleVoiceListen} title="Dictate Query">
                    <MicIcon />
                </button>
            )}
          </div>

          <button type="submit" className="send-button" disabled={isLoading || !query.trim() || !activeConversationId}>
            Send
          </button>
        </form>
      </div>
    </div>
  )
}