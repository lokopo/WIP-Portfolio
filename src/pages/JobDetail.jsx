import React, { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useJobs } from '../contexts/JobContext'
import { 
  ArrowLeft, 
  Edit, 
  Save, 
  X,
  MapPin,
  DollarSign,
  Calendar,
  Mail,
  Phone,
  ExternalLink,
  FileText,
  User
} from 'lucide-react'
import { format } from 'date-fns'

const JobDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { jobs, updateJob, deleteJob } = useJobs()
  const [isEditing, setIsEditing] = useState(false)
  
  const job = jobs.find(j => j.id === id)
  
  const [formData, setFormData] = useState(job || {})

  if (!job) {
    return (
      <div className="p-8">
        <div className="card text-center py-12">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Job not found</h2>
          <p className="text-gray-600 mb-4">The job application you're looking for doesn't exist.</p>
          <button
            onClick={() => navigate('/jobs')}
            className="btn-primary"
          >
            Back to Jobs
          </button>
        </div>
      </div>
    )
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSave = () => {
    updateJob(id, formData)
    setIsEditing(false)
  }

  const handleCancel = () => {
    setFormData(job)
    setIsEditing(false)
  }

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this job application? This action cannot be undone.')) {
      deleteJob(id)
      navigate('/jobs')
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'applied': return 'bg-blue-100 text-blue-800'
      case 'interviewing': return 'bg-yellow-100 text-yellow-800'
      case 'offered': return 'bg-green-100 text-green-800'
      case 'rejected': return 'bg-red-100 text-red-800'
      case 'withdrawn': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <button
          onClick={() => navigate('/jobs')}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Jobs
        </button>
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {isEditing ? (
                <input
                  type="text"
                  name="position"
                  value={formData.position}
                  onChange={handleChange}
                  className="input-field text-3xl font-bold"
                />
              ) : (
                job.position
              )}
            </h1>
            <p className="text-xl text-gray-600">
              {isEditing ? (
                <input
                  type="text"
                  name="company"
                  value={formData.company}
                  onChange={handleChange}
                  className="input-field text-xl"
                />
              ) : (
                job.company
              )}
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            {!isEditing && (
              <>
                <button
                  onClick={() => setIsEditing(true)}
                  className="btn-secondary inline-flex items-center"
                >
                  <Edit className="w-4 h-4 mr-2" />
                  Edit
                </button>
                <button
                  onClick={handleDelete}
                  className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 inline-flex items-center"
                >
                  Delete
                </button>
              </>
            )}
            {isEditing && (
              <>
                <button
                  onClick={handleCancel}
                  className="btn-secondary inline-flex items-center"
                >
                  <X className="w-4 h-4 mr-2" />
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  className="btn-primary inline-flex items-center"
                >
                  <Save className="w-4 h-4 mr-2" />
                  Save
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Status and Key Info */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Application Details</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                {isEditing ? (
                  <select
                    name="status"
                    value={formData.status}
                    onChange={handleChange}
                    className="input-field"
                  >
                    <option value="applied">Applied</option>
                    <option value="interviewing">Interviewing</option>
                    <option value="offered">Offered</option>
                    <option value="rejected">Rejected</option>
                    <option value="withdrawn">Withdrawn</option>
                  </select>
                ) : (
                  <div className={`px-3 py-2 rounded-lg text-sm font-medium inline-block ${getStatusColor(job.status)}`}>
                    {job.status}
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Applied Date</label>
                {isEditing ? (
                  <input
                    type="date"
                    name="appliedDate"
                    value={formData.appliedDate}
                    onChange={handleChange}
                    className="input-field"
                  />
                ) : (
                  <div className="flex items-center text-gray-900">
                    <Calendar className="w-4 h-4 mr-2" />
                    {format(new Date(job.appliedDate || job.createdAt), 'MMMM dd, yyyy')}
                  </div>
                )}
              </div>

              {job.location && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
                  {isEditing ? (
                    <input
                      type="text"
                      name="location"
                      value={formData.location}
                      onChange={handleChange}
                      className="input-field"
                    />
                  ) : (
                    <div className="flex items-center text-gray-900">
                      <MapPin className="w-4 h-4 mr-2" />
                      {job.location}
                    </div>
                  )}
                </div>
              )}

              {job.salary && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Salary</label>
                  {isEditing ? (
                    <input
                      type="text"
                      name="salary"
                      value={formData.salary}
                      onChange={handleChange}
                      className="input-field"
                    />
                  ) : (
                    <div className="flex items-center text-gray-900">
                      <DollarSign className="w-4 h-4 mr-2" />
                      {job.salary}
                    </div>
                  )}
                </div>
              )}
            </div>

            {job.applicationUrl && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Application URL</label>
                {isEditing ? (
                  <input
                    type="url"
                    name="applicationUrl"
                    value={formData.applicationUrl}
                    onChange={handleChange}
                    className="input-field"
                  />
                ) : (
                  <a
                    href={job.applicationUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:text-primary-700 inline-flex items-center"
                  >
                    <ExternalLink className="w-4 h-4 mr-2" />
                    View Application
                  </a>
                )}
              </div>
            )}
          </div>

          {/* Job Description */}
          {(job.jobDescription || isEditing) && (
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Job Description</h2>
              {isEditing ? (
                <textarea
                  name="jobDescription"
                  value={formData.jobDescription}
                  onChange={handleChange}
                  rows={8}
                  className="input-field"
                  placeholder="Paste the job description here..."
                />
              ) : (
                <div className="prose max-w-none">
                  <p className="text-gray-700 whitespace-pre-wrap">{job.jobDescription}</p>
                </div>
              )}
            </div>
          )}

          {/* Notes */}
          {(job.notes || isEditing) && (
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Notes</h2>
              {isEditing ? (
                <textarea
                  name="notes"
                  value={formData.notes}
                  onChange={handleChange}
                  rows={4}
                  className="input-field"
                  placeholder="Add any notes or reminders..."
                />
              ) : (
                <div className="prose max-w-none">
                  <p className="text-gray-700 whitespace-pre-wrap">{job.notes}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Contact Information */}
          {(job.contactPerson || job.contactEmail || job.contactPhone || isEditing) && (
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Contact Information</h2>
              
              <div className="space-y-4">
                {isEditing ? (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Contact Person</label>
                      <input
                        type="text"
                        name="contactPerson"
                        value={formData.contactPerson}
                        onChange={handleChange}
                        className="input-field"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                      <input
                        type="email"
                        name="contactEmail"
                        value={formData.contactEmail}
                        onChange={handleChange}
                        className="input-field"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
                      <input
                        type="tel"
                        name="contactPhone"
                        value={formData.contactPhone}
                        onChange={handleChange}
                        className="input-field"
                      />
                    </div>
                  </>
                ) : (
                  <>
                    {job.contactPerson && (
                      <div className="flex items-center text-gray-700">
                        <User className="w-4 h-4 mr-3 text-gray-400" />
                        <span>{job.contactPerson}</span>
                      </div>
                    )}
                    {job.contactEmail && (
                      <div className="flex items-center text-gray-700">
                        <Mail className="w-4 h-4 mr-3 text-gray-400" />
                        <a href={`mailto:${job.contactEmail}`} className="text-primary-600 hover:text-primary-700">
                          {job.contactEmail}
                        </a>
                      </div>
                    )}
                    {job.contactPhone && (
                      <div className="flex items-center text-gray-700">
                        <Phone className="w-4 h-4 mr-3 text-gray-400" />
                        <a href={`tel:${job.contactPhone}`} className="text-primary-600 hover:text-primary-700">
                          {job.contactPhone}
                        </a>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          )}

          {/* Documents Used */}
          {(job.resumeUsed || job.coverLetterUsed || isEditing) && (
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Documents Used</h2>
              
              <div className="space-y-4">
                {isEditing ? (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Resume</label>
                      <input
                        type="text"
                        name="resumeUsed"
                        value={formData.resumeUsed}
                        onChange={handleChange}
                        className="input-field"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Cover Letter</label>
                      <input
                        type="text"
                        name="coverLetterUsed"
                        value={formData.coverLetterUsed}
                        onChange={handleChange}
                        className="input-field"
                      />
                    </div>
                  </>
                ) : (
                  <>
                    {job.resumeUsed && (
                      <div className="flex items-center text-gray-700">
                        <FileText className="w-4 h-4 mr-3 text-gray-400" />
                        <span>{job.resumeUsed}</span>
                      </div>
                    )}
                    {job.coverLetterUsed && (
                      <div className="flex items-center text-gray-700">
                        <FileText className="w-4 h-4 mr-3 text-gray-400" />
                        <span>{job.coverLetterUsed}</span>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          )}

          {/* Timeline */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Timeline</h2>
            <div className="space-y-3">
              <div className="flex items-center text-sm text-gray-600">
                <div className="w-2 h-2 bg-primary-600 rounded-full mr-3"></div>
                <span>Created: {format(new Date(job.createdAt), 'MMM dd, yyyy')}</span>
              </div>
              {job.updatedAt && (
                <div className="flex items-center text-sm text-gray-600">
                  <div className="w-2 h-2 bg-gray-400 rounded-full mr-3"></div>
                  <span>Updated: {format(new Date(job.updatedAt), 'MMM dd, yyyy')}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default JobDetail