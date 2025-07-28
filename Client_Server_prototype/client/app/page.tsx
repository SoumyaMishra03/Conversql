"use client"

import { useState, useEffect } from "react"
import LoginForm from "@/components/login-form"
import Dashboard from "@/components/dashboard"
import type { Session } from "@/types/session"

export default function Home() {
  const [session, setSession] = useState<Session | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check for existing session in localStorage
    const savedSession = localStorage.getItem("session")
    if (savedSession) {
      try {
        setSession(JSON.parse(savedSession))
      } catch (error) {
        localStorage.removeItem("session")
      }
    }
    setIsLoading(false)
  }, [])

  const handleLogin = (newSession: Session) => {
    setSession(newSession)
    localStorage.setItem("session", JSON.stringify(newSession))
  }

  const handleLogout = () => {
    setSession(null)
    localStorage.removeItem("session")
  }

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    )
  }

  return (
    <main className="app">
      {session ? <Dashboard session={session} onLogout={handleLogout} /> : <LoginForm onLogin={handleLogin} />}
    </main>
  )
}
