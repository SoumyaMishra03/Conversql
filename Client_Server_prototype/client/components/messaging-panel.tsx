"use client"

import type React from "react"
import { useState, useEffect, useRef } from "react"
import type { Session } from "@/types/session"
import "./messaging-panel.css"
import { API_BASE_URL } from "@/config/api"

// --- Helper Icons ---
const SendIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
);
const AttachmentIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
);
// --- End Helper Icons ---

interface Message {
  id: number
  from: string
  to?: string
  message: string
  time: string
}

interface User {
  username: string;
  lastMessage: string;
  lastMessageTimestamp: string;
}

interface MessagingPanelProps {
  session: Session
}

// Helper function to check if a message is a file share
const isFileShare = (message: string) => {
  return message.startsWith("Shared a file:");
};

// Helper function to extract filename
const getFilename = (message: string) => {
  return message.replace("Shared a file: ", "");
};


export default function MessagingPanel({ session }: MessagingPanelProps) {
  const [users, setUsers] = useState<User[]>([]);
  const [activeChatUser, setActiveChatUser] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [isSending, setIsSending] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const isAdmin = session.role === 'admin';

  const fetchUsers = async () => {
    if (!isAdmin) return;
    try {
      const response = await fetch(`${API_BASE_URL}/admin/conversations?admin_user=${session.username}&admin_pass=${session.password}`);
      if (response.ok) {
        const data = await response.json();
        setUsers(data.conversations || []);
        if (!activeChatUser && data.conversations.length > 0) {
          setActiveChatUser(data.conversations[0].username);
        }
      }
    } catch (error) {
      console.error("Failed to fetch users:", error);
    }
  };

  const fetchMessages = async (username: string) => {
    const endpoint = isAdmin 
      ? `${API_BASE_URL}/admin/conversation/${username}?admin_user=${session.username}&admin_pass=${session.password}`
      : `${API_BASE_URL}/messages?username=${session.username}&password=${session.password}`;

    try {
      const response = await fetch(endpoint);
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages || []);
      }
    } catch (error) {
      console.error(`Failed to fetch messages for ${username}:`, error);
    }
  };

  useEffect(() => {
    if (isAdmin) {
      fetchUsers();
    } else {
      setActiveChatUser("admin");
    }
  }, [isAdmin]);

  useEffect(() => {
    if (activeChatUser) {
      fetchMessages(activeChatUser);
      const interval = setInterval(() => fetchMessages(activeChatUser), 5000);
      return () => clearInterval(interval);
    } else {
      setMessages([]);
    }
  }, [activeChatUser]);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);
  
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || !activeChatUser) return;
    setIsSending(true);

    const endpoint = isAdmin ? `${API_BASE_URL}/admin/message` : `${API_BASE_URL}/message`;
    const body = isAdmin ? {
      admin_user: session.username,
      admin_pass: session.password,
      target_user: activeChatUser,
      message: newMessage,
    } : {
      username: session.username,
      password: session.password,
      message: newMessage,
    };

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (response.ok) {
        setNewMessage("");
        fetchMessages(activeChatUser);
      }
    } catch (error) {
      console.error("Failed to send message:", error);
    } finally {
      setIsSending(false);
    }
  };
  
  const handleAttachmentClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && activeChatUser) {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('username', session.username);
      formData.append('password', session.password);
      formData.append('target_user', isAdmin ? activeChatUser : 'admin');

      try {
        const response = await fetch(`${API_BASE_URL}/upload-document`, {
          method: 'POST',
          body: formData,
        });
        if (response.ok) {
          alert(`File '${file.name}' sent successfully!`);
          fetchMessages(activeChatUser);
        } else {
          alert('File upload failed.');
        }
      } catch (error) {
        console.error("File upload error:", error);
        alert("An error occurred during file upload.");
      }
    }
  };

  const renderSidebar = () => {
    if (!isAdmin) return null;
    return (
      <div className="chat-sidebar">
        <div className="sidebar-header">
          <h3>Conversations</h3>
        </div>
        <div className="user-list">
          {users.map(user => (
            <div 
              key={user.username} 
              className={`user-list-item ${user.username === activeChatUser ? 'active' : ''}`}
              onClick={() => setActiveChatUser(user.username)}
            >
              <div className="user-avatar">{user.username.charAt(0).toUpperCase()}</div>
              <div className="user-info">
                <span className="user-name">{user.username}</span>
                <span className="last-message">{user.lastMessage}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className={`messaging-panel-layout ${!isAdmin ? 'user-view' : ''}`}>
      {renderSidebar()}
      
      <div className="live-chat-panel">
        {activeChatUser ? (
          <>
            <div className="chat-header">
              <h2>{activeChatUser}</h2>
              <p>Live conversation</p>
            </div>
            <div className="live-chat-container" ref={chatContainerRef}>
              {messages.map((msg) => (
                <div key={msg.id} className={`live-chat-bubble-wrapper ${msg.from === session.username ? 'self' : 'other'}`}>
                  <div className="bubble-header">{msg.from}</div>
                  <div className="live-chat-bubble">
                    {isFileShare(msg.message) ? (
                      <a 
                        href={`${API_BASE_URL}/download-document/${getFilename(msg.message)}`} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="file-link"
                      >
                        {getFilename(msg.message)}
                      </a>
                    ) : (
                      <p className="message-text">{msg.message}</p>
                    )}
                    <span className="message-time">
                      {/* FIXED: Added a check to prevent crash on invalid date */}
                      {(msg.time && typeof msg.time === 'string') 
                        ? new Date(msg.time.replace(' ', 'T')).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
                        : '...'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <form onSubmit={handleSendMessage} className="message-input-form">
              <input type="file" ref={fileInputRef} style={{ display: 'none' }} onChange={handleFileChange} />
              <button type="button" className="attachment-button" onClick={handleAttachmentClick}>
                <AttachmentIcon />
              </button>
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type your message here..."
                disabled={isSending}
              />
              <button type="submit" className="send-button" disabled={isSending || !newMessage.trim()}>
                <SendIcon />
              </button>
            </form>
          </>
        ) : (
          <div className="no-chat-selected">
            {isAdmin ? "Select a conversation to start chatting." : "Send a message to the admin to start a conversation."}
          </div>
        )}
      </div>
    </div>
  );
}