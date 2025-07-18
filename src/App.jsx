import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { JobProvider } from './contexts/JobContext'
import { ThemeProvider } from './contexts/ThemeContext'
import { NotificationProvider } from './contexts/NotificationContext'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import JobList from './pages/JobList'
import AddJob from './pages/AddJob'
import JobDetail from './pages/JobDetail'
import Documents from './pages/Documents'
import Settings from './pages/Settings'

function App() {
  return (
    <ThemeProvider>
      <JobProvider>
        <NotificationProvider>
          <Router>
            <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
              <Sidebar />
              <main className="flex-1 overflow-auto">
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/jobs" element={<JobList />} />
                  <Route path="/jobs/add" element={<AddJob />} />
                  <Route path="/jobs/:id" element={<JobDetail />} />
                  <Route path="/documents" element={<Documents />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </main>
            </div>
          </Router>
        </NotificationProvider>
      </JobProvider>
    </ThemeProvider>
  )
}

export default App