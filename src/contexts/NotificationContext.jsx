import React, { createContext, useContext, useState, useEffect } from 'react'
import { useJobs } from './JobContext'

const NotificationContext = createContext()

export const NotificationProvider = ({ children }) => {
  const { jobs } = useJobs()
  const [notifications, setNotifications] = useState([])
  const [showNotifications, setShowNotifications] = useState(false)

  // Check for follow-up reminders
  useEffect(() => {
    const checkFollowUps = () => {
      const today = new Date()
      const newNotifications = []

      jobs.forEach(job => {
        // Check if job needs follow-up (7 days after application)
        const appliedDate = new Date(job.appliedDate || job.createdAt)
        const daysSinceApplied = Math.floor((today - appliedDate) / (1000 * 60 * 60 * 24))
        
        if (daysSinceApplied >= 7 && job.status === 'applied') {
          newNotifications.push({
            id: `followup-${job.id}`,
            type: 'followup',
            title: 'Follow-up Reminder',
            message: `It's been ${daysSinceApplied} days since you applied to ${job.company}. Consider sending a follow-up email.`,
            jobId: job.id,
            timestamp: new Date().toISOString(),
            read: false
          })
        }

        // Check for interview reminders
        if (job.interviewDate) {
          const interviewDate = new Date(job.interviewDate)
          const daysUntilInterview = Math.floor((interviewDate - today) / (1000 * 60 * 60 * 24))
          
          if (daysUntilInterview === 1) {
            newNotifications.push({
              id: `interview-${job.id}`,
              type: 'interview',
              title: 'Interview Tomorrow',
              message: `You have an interview tomorrow with ${job.company} for the ${job.position} position.`,
              jobId: job.id,
              timestamp: new Date().toISOString(),
              read: false
            })
          }
        }
      })

      setNotifications(prev => {
        const existingIds = prev.map(n => n.id)
        const filteredNew = newNotifications.filter(n => !existingIds.includes(n.id))
        return [...prev, ...filteredNew]
      })
    }

    checkFollowUps()
    // Check every hour
    const interval = setInterval(checkFollowUps, 60 * 60 * 1000)
    
    return () => clearInterval(interval)
  }, [jobs])

  const markAsRead = (notificationId) => {
    setNotifications(prev => 
      prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
    )
  }

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })))
  }

  const deleteNotification = (notificationId) => {
    setNotifications(prev => prev.filter(n => n.id !== notificationId))
  }

  const addNotification = (notification) => {
    setNotifications(prev => [...prev, {
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      read: false,
      ...notification
    }])
  }

  const unreadCount = notifications.filter(n => !n.read).length

  const value = {
    notifications,
    unreadCount,
    showNotifications,
    setShowNotifications,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    addNotification
  }

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  )
}

export const useNotifications = () => {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider')
  }
  return context
}