import React from 'react'
import { useJobs } from '../contexts/JobContext'

const AnalyticsChart = () => {
  const { jobs } = useJobs()

  const stats = {
    total: jobs.length,
    applied: jobs.filter(job => job.status === 'applied').length,
    interviewing: jobs.filter(job => job.status === 'interviewing').length,
    offered: jobs.filter(job => job.status === 'offered').length,
    rejected: jobs.filter(job => job.status === 'rejected').length,
    withdrawn: jobs.filter(job => job.status === 'withdrawn').length,
  }

  const total = stats.total || 1 // Avoid division by zero

  const getStatusColor = (status) => {
    switch (status) {
      case 'applied': return 'bg-blue-500'
      case 'interviewing': return 'bg-yellow-500'
      case 'offered': return 'bg-green-500'
      case 'rejected': return 'bg-red-500'
      case 'withdrawn': return 'bg-gray-500'
      default: return 'bg-gray-400'
    }
  }

  const getStatusLabel = (status) => {
    switch (status) {
      case 'applied': return 'Applied'
      case 'interviewing': return 'Interviewing'
      case 'offered': return 'Offered'
      case 'rejected': return 'Rejected'
      case 'withdrawn': return 'Withdrawn'
      default: return status
    }
  }

  const statusData = [
    { key: 'applied', ...stats },
    { key: 'interviewing', ...stats },
    { key: 'offered', ...stats },
    { key: 'rejected', ...stats },
    { key: 'withdrawn', ...stats },
  ].filter(item => item[item.key] > 0)

  // Calculate monthly applications
  const monthlyData = jobs.reduce((acc, job) => {
    const date = new Date(job.createdAt)
    const monthYear = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
    acc[monthYear] = (acc[monthYear] || 0) + 1
    return acc
  }, {})

  const recentMonths = Object.keys(monthlyData)
    .sort()
    .slice(-6) // Last 6 months

  return (
    <div className="space-y-6">
      {/* Status Distribution */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Application Status Distribution
        </h3>
        <div className="space-y-3">
          {statusData.map((item) => {
            const percentage = Math.round((item[item.key] / total) * 100)
            return (
              <div key={item.key} className="flex items-center">
                <div className="w-24 text-sm text-gray-600 dark:text-gray-400">
                  {getStatusLabel(item.key)}
                </div>
                <div className="flex-1 mx-4">
                  <div className="bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${getStatusColor(item.key)}`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
                <div className="w-16 text-sm font-medium text-gray-900 dark:text-white text-right">
                  {item[item.key]} ({percentage}%)
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Monthly Applications */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Applications by Month
        </h3>
        <div className="flex items-end space-x-2 h-32">
          {recentMonths.map((month) => {
            const count = monthlyData[month]
            const maxCount = Math.max(...Object.values(monthlyData))
            const height = maxCount > 0 ? (count / maxCount) * 100 : 0
            
            return (
              <div key={month} className="flex-1 flex flex-col items-center">
                <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                  {count}
                </div>
                <div
                  className="w-full bg-primary-500 rounded-t"
                  style={{ height: `${height}%` }}
                />
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {new Date(month + '-01').toLocaleDateString('en-US', { 
                    month: 'short',
                    year: '2-digit'
                  })}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card text-center">
          <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
            {stats.total}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Total Applications
          </div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">
            {stats.offered}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Offers Received
          </div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {stats.interviewing}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            In Progress
          </div>
        </div>
      </div>
    </div>
  )
}

export default AnalyticsChart