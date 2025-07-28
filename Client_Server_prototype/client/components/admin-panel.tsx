"use client"

import type React from "react"
import { useState, useEffect } from "react"
import type { Session } from "@/types/session"
import "./admin-panel.css"
import { API_BASE_URL } from "@/config/api"

interface AdminPanelProps {
  session: Session
}

type AdminTab = "users" | "messages" | "logs"

export default function AdminPanel({ session }: AdminPanelProps) {
  const [activeTab, setActiveTab] = useState<AdminTab>("users")
  const [logs, setLogs] = useState<any[]>([])
  const [allMessages, setAllMessages] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)

  // User management states
  const [newUsername, setNewUsername] = useState("")
  const [newDepartment, setNewDepartment] = useState("")
  const [newPosition, setNewPosition] = useState("")
  const [lockUsername, setLockUsername] = useState("")
  const [lockDuration, setLockDuration] = useState("")

  // Messaging states
  const [messageTarget, setMessageTarget] = useState("")
  const [messageContent, setMessageContent] = useState("")

  useEffect(() => {
    if (activeTab === "logs") {
      fetchLogs()
    } else if (activeTab === "messages") {
      fetchAllMessages()
    }
  }, [activeTab])

  const fetchLogs = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(
        `${API_BASE_URL}/logs/access?admin_user=${session.username}&admin_pass=${session.password}`,
      )
      if (response.ok) {
        const data = await response.json()
        setLogs(data.logs || [])
      }
    } catch (error) {
      console.error("Failed to fetch logs:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchAllMessages = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(
        `${API_BASE_URL}/admin/messages?admin_user=${session.username}&admin_pass=${session.password}`,
      )
      if (response.ok) {
        const data = await response.json()
        setAllMessages(data.messages || [])
      }
    } catch (error) {
      console.error("Failed to fetch messages:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const addUser = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await fetch(`${API_BASE_URL}/admin/add_user`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          admin_user: session.username,
          admin_pass: session.password,
          target_user: newUsername,
          department: newDepartment,
          position: newPosition,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        alert(`User created successfully!\nUsername: ${data.username}\nPassword: ${data.password}`)
        setNewUsername("")
        setNewDepartment("")
        setNewPosition("")
      } else {
        const error = await response.json()
        alert(`Error: ${error.detail}`)
      }
    } catch (error) {
      alert("Failed to create user")
    }
  }

  const lockUser = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await fetch(`${API_BASE_URL}/admin/lock`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          admin_user: session.username,
          admin_pass: session.password,
          target_user: lockUsername,
          duration_minutes: Number.parseInt(lockDuration),
        }),
      })

      if (response.ok) {
        const data = await response.json()
        alert(`User ${data.locked_user} locked until ${data.until}`)
        setLockUsername("")
        setLockDuration("")
      } else {
        const error = await response.json()
        alert(`Error: ${error.detail}`)
      }
    } catch (error) {
      alert("Failed to lock user")
    }
  }

  const sendMessageToUser = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await fetch(`${API_BASE_URL}/admin/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          admin_user: session.username,
          admin_pass: session.password,
          target_user: messageTarget,
          message: messageContent,
        }),
      })

      if (response.ok) {
        alert("Message sent successfully!")
        setMessageTarget("")
        setMessageContent("")
        fetchAllMessages()
      } else {
        const error = await response.json()
        alert(`Error: ${error.detail}`)
      }
    } catch (error) {
      alert("Failed to send message")
    }
  }

  return (
    <div className="admin-panel">
      <div className="panel-header">
        <h2>Admin Panel</h2>
      </div>

      <div className="admin-tabs">
        <button className={`tab-button ${activeTab === "users" ? "active" : ""}`} onClick={() => setActiveTab("users")}>
          User Management
        </button>
        <button
          className={`tab-button ${activeTab === "messages" ? "active" : ""}`}
          onClick={() => setActiveTab("messages")}
        >
          All Messages
        </button>
        <button className={`tab-button ${activeTab === "logs" ? "active" : ""}`} onClick={() => setActiveTab("logs")}>
          Access Logs
        </button>
      </div>

      <div className="tab-content">
        {activeTab === "users" && (
          <div className="users-tab">
            <div className="admin-section">
              <h3>Add New User</h3>
              <form onSubmit={addUser} className="admin-form">
                <div className="form-row">
                  <input
                    type="text"
                    placeholder="Username"
                    value={newUsername}
                    onChange={(e) => setNewUsername(e.target.value)}
                    required
                  />
                  <input
                    type="text"
                    placeholder="Department"
                    value={newDepartment}
                    onChange={(e) => setNewDepartment(e.target.value)}
                    required
                  />
                  <input
                    type="text"
                    placeholder="Position"
                    value={newPosition}
                    onChange={(e) => setNewPosition(e.target.value)}
                    required
                  />
                </div>
                <button type="submit" className="admin-button">
                  Add User
                </button>
              </form>
            </div>

            <div className="admin-section">
              <h3>Lock User</h3>
              <form onSubmit={lockUser} className="admin-form">
                <div className="form-row">
                  <input
                    type="text"
                    placeholder="Username to lock"
                    value={lockUsername}
                    onChange={(e) => setLockUsername(e.target.value)}
                    required
                  />
                  <input
                    type="number"
                    placeholder="Duration (minutes)"
                    value={lockDuration}
                    onChange={(e) => setLockDuration(e.target.value)}
                    required
                  />
                </div>
                <button type="submit" className="admin-button danger">
                  Lock User
                </button>
              </form>
            </div>
          </div>
        )}

        {activeTab === "messages" && (
          <div className="messages-tab">
            <div className="admin-section">
              <h3>Send Message to User</h3>
              <form onSubmit={sendMessageToUser} className="admin-form">
                <div className="form-row">
                  <input
                    type="text"
                    placeholder="Username"
                    value={messageTarget}
                    onChange={(e) => setMessageTarget(e.target.value)}
                    required
                  />
                </div>
                <textarea
                  placeholder="Message content"
                  value={messageContent}
                  onChange={(e) => setMessageContent(e.target.value)}
                  rows={3}
                  required
                />
                <button type="submit" className="admin-button">
                  Send Message
                </button>
              </form>
            </div>

            <div className="admin-section">
              <div className="section-header">
                <h3>All Messages</h3>
                <button onClick={fetchAllMessages} className="refresh-button" disabled={isLoading}>
                  {isLoading ? "Loading..." : "Refresh"}
                </button>
              </div>
              <div className="data-list">
                {allMessages.map((msg, index) => (
                  <div key={index} className="data-item">
                    <div className="message-info">
                      <strong>
                        {msg.from} → {msg.to}
                      </strong>
                      <span className="timestamp">{msg.time}</span>
                    </div>
                    <div className="message-text">{msg.message}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === "logs" && (
          <div className="logs-tab">
            <div className="admin-section">
              <div className="section-header">
                <h3>Access Logs</h3>
                <button onClick={fetchLogs} className="refresh-button" disabled={isLoading}>
                  {isLoading ? "Loading..." : "Refresh"}
                </button>
              </div>
              <div className="data-list">
                {logs.map((log, index) => (
                  <div key={index} className="data-item">
                    <div className="log-info">
                      <strong>{log.username}</strong>
                      {/* FIXED: Check if log.action exists before calling toLowerCase */}
                      <span className={`action ${(log.action || '').toLowerCase()}`}>
                        {log.action || 'NO_ACTION'}
                      </span>
                      <span className="timestamp">{log.timestamp}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}