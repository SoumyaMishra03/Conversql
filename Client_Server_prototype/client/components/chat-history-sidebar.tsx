"use client"

import type React from 'react';
import type { Conversation } from './query-panel';
import './chat-history-sidebar.css';

interface ChatHistorySidebarProps {
  conversations: Conversation[];
  activeConversationId: string | null;
  onNewChat: () => void;
  onSelectChat: (id: string) => void;
  onDeleteChat: (id: string) => void;
}

const ChatIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const DeleteIcon = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 6h18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
);


export default function ChatHistorySidebar({
  conversations,
  activeConversationId,
  onNewChat,
  onSelectChat,
  onDeleteChat,
}: ChatHistorySidebarProps) {
  return (
    <div className="chat-history-sidebar">
      <div className="sidebar-header">
        <h3>History</h3>
        <button onClick={onNewChat} className="new-chat-button">+</button>
      </div>
      <div className="conversation-list">
        {conversations.map((conv) => (
          <div
            key={conv.id}
            className={`conversation-item ${conv.id === activeConversationId ? 'active' : ''}`}
            onClick={() => onSelectChat(conv.id)}
          >
            <ChatIcon />
            <span className="conversation-title">{conv.title}</span>
            <button 
              className="delete-chat-button"
              onClick={(e) => {
                e.stopPropagation(); // Prevent selecting the chat
                onDeleteChat(conv.id);
              }}
            >
              <DeleteIcon />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}