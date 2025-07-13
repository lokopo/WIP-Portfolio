import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useJobs } from '../contexts/JobContext'
import { ArrowLeft, Save, Plus } from 'lucide-react'

const AddJob = () => {
  const navigate = useNavigate()
  const { addJob } = useJobs()
  const [formData, setFormData] = useState({
    company: '',
    position: '',
    location: '',
    salary: '',
    jobDescription: '',
    applicationUrl: '',
    contactPerson: '',
    contactEmail: '',
    contactPhone: '',
    notes: '',
    status: 'applied',
    appliedDate: new Date().toISOString().split('T')[0],
    resumeUsed: '',
    coverLetterUsed: '',
    otherDocuments: []
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    addJob(formData)
    navigate('/jobs')
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
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Add New Job Application</h1>
        <p className="text-gray-600">Track a new job application with all relevant details</p>
      </div>

      <form onSubmit={handleSubmit} className="max-w-4xl">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Basic Information */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Basic Information</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Name *
                </label>
                <input
                  type="text"
                  name="company"
                  value={formData.company}
                  onChange={handleChange}
                  required
                  className="input-field"
                  placeholder="Enter company name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Position Title *
                </label>
                <input
                  type="text"
                  name="position"
                  value={formData.position}
                  onChange={handleChange}
                  required
                  className="input-field"
                  placeholder="Enter position title"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location
                </label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleChange}
                  className="input-field"
                  placeholder="City, State or Remote"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Salary Range
                </label>
                <input
                  type="text"
                  name="salary"
                  value={formData.salary}
                  onChange={handleChange}
                  className="input-field"
                  placeholder="e.g., $50,000 - $70,000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Application Status
                </label>
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
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Applied Date
                </label>
                <input
                  type="date"
                  name="appliedDate"
                  value={formData.appliedDate}
                  onChange={handleChange}
                  className="input-field"
                />
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Contact Information</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Contact Person
                </label>
                <input
                  type="text"
                  name="contactPerson"
                  value={formData.contactPerson}
                  onChange={handleChange}
                  className="input-field"
                  placeholder="Hiring manager name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Contact Email
                </label>
                <input
                  type="email"
                  name="contactEmail"
                  value={formData.contactEmail}
                  onChange={handleChange}
                  className="input-field"
                  placeholder="contact@company.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Contact Phone
                </label>
                <input
                  type="tel"
                  name="contactPhone"
                  value={formData.contactPhone}
                  onChange={handleChange}
                  className="input-field"
                  placeholder="+1 (555) 123-4567"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Application URL
                </label>
                <input
                  type="url"
                  name="applicationUrl"
                  value={formData.applicationUrl}
                  onChange={handleChange}
                  className="input-field"
                  placeholder="https://company.com/careers/position"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Job Description */}
        <div className="card mt-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Job Description</h2>
          <textarea
            name="jobDescription"
            value={formData.jobDescription}
            onChange={handleChange}
            rows={6}
            className="input-field"
            placeholder="Paste the job description here or add your notes about the role..."
          />
        </div>

        {/* Documents Used */}
        <div className="card mt-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Documents Used</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Resume Used
              </label>
              <input
                type="text"
                name="resumeUsed"
                value={formData.resumeUsed}
                onChange={handleChange}
                className="input-field"
                placeholder="e.g., Software Engineer Resume v2"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cover Letter Used
              </label>
              <input
                type="text"
                name="coverLetterUsed"
                value={formData.coverLetterUsed}
                onChange={handleChange}
                className="input-field"
                placeholder="e.g., Cover Letter - Tech Companies"
              />
            </div>
          </div>
        </div>

        {/* Notes */}
        <div className="card mt-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Additional Notes</h2>
          <textarea
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            rows={4}
            className="input-field"
            placeholder="Add any additional notes, follow-up reminders, or important details..."
          />
        </div>

        {/* Form Actions */}
        <div className="flex justify-end space-x-4 mt-8">
          <button
            type="button"
            onClick={() => navigate('/jobs')}
            className="btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn-primary inline-flex items-center"
          >
            <Save className="w-4 h-4 mr-2" />
            Save Application
          </button>
        </div>
      </form>
    </div>
  )
}

export default AddJob