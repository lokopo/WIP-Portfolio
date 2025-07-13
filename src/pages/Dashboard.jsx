import React from 'react'
import { Link } from 'react-router-dom'
import { useJobs } from '../contexts/JobContext'
import { 
  Briefcase, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Plus,
  TrendingUp,
  Calendar,
  FileText
} from 'lucide-react'
import { format } from 'date-fns'

const Dashboard = () => {
  const { jobs, documents } = useJobs()

  const stats = {
    total: jobs.length,
    applied: jobs.filter(job => job.status === 'applied').length,
    interviewing: jobs.filter(job => job.status === 'interviewing').length,
    rejected: jobs.filter(job => job.status === 'rejected').length,
    offered: jobs.filter(job => job.status === 'offered').length,
  }

  const recentJobs = jobs
    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
    .slice(0, 5)

  const getStatusColor = (status) => {
    switch (status) {
      case 'applied': return 'bg-blue-100 text-blue-800'
      case 'interviewing': return 'bg-yellow-100 text-yellow-800'
      case 'offered': return 'bg-green-100 text-green-800'
      case 'rejected': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'applied': return <Clock className="w-4 h-4" />
      case 'interviewing': return <TrendingUp className="w-4 h-4" />
      case 'offered': return <CheckCircle className="w-4 h-4" />
      case 'rejected': return <XCircle className="w-4 h-4" />
      default: return <Clock className="w-4 h-4" />
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Track your job application progress</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Briefcase className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Applications</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Clock className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Applied</p>
              <p className="text-2xl font-bold text-gray-900">{stats.applied}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Interviewing</p>
              <p className="text-2xl font-bold text-gray-900">{stats.interviewing}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Offered</p>
              <p className="text-2xl font-bold text-gray-900">{stats.offered}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-red-100 rounded-lg">
              <XCircle className="w-6 h-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Rejected</p>
              <p className="text-2xl font-bold text-gray-900">{stats.rejected}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Applications */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Recent Applications</h2>
            <Link to="/jobs" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
              View all
            </Link>
          </div>
          
          {recentJobs.length === 0 ? (
            <div className="text-center py-8">
              <Briefcase className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">No job applications yet</p>
              <Link to="/jobs/add" className="btn-primary inline-flex items-center">
                <Plus className="w-4 h-4 mr-2" />
                Add your first job
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {recentJobs.map((job) => (
                <div key={job.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{job.company}</h3>
                    <p className="text-sm text-gray-600">{job.position}</p>
                    <div className="flex items-center mt-1">
                      <Calendar className="w-3 h-3 text-gray-400 mr-1" />
                      <span className="text-xs text-gray-500">
                        {format(new Date(job.createdAt), 'MMM dd, yyyy')}
                      </span>
                    </div>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium flex items-center ${getStatusColor(job.status)}`}>
                    {getStatusIcon(job.status)}
                    <span className="ml-1 capitalize">{job.status}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Documents Overview */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Documents</h2>
            <Link to="/documents" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
              Manage
            </Link>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <FileText className="w-5 h-5 text-gray-600 mr-3" />
                <div>
                  <p className="font-medium text-gray-900">Resumes</p>
                  <p className="text-sm text-gray-600">{documents.filter(d => d.type === 'resume').length} files</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <FileText className="w-5 h-5 text-gray-600 mr-3" />
                <div>
                  <p className="font-medium text-gray-900">Cover Letters</p>
                  <p className="text-sm text-gray-600">{documents.filter(d => d.type === 'cover-letter').length} files</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <FileText className="w-5 h-5 text-gray-600 mr-3" />
                <div>
                  <p className="font-medium text-gray-900">Other Documents</p>
                  <p className="text-sm text-gray-600">{documents.filter(d => d.type === 'other').length} files</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard