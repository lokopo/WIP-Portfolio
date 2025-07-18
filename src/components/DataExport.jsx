import React, { useState } from 'react'
import { useJobs } from '../contexts/JobContext'
import { Download, Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react'

const DataExport = () => {
  const { jobs, documents, addJob, addDocument } = useJobs()
  const [importStatus, setImportStatus] = useState(null)
  const [importMessage, setImportMessage] = useState('')

  const exportData = (format) => {
    const data = {
      jobs,
      documents,
      exportDate: new Date().toISOString(),
      version: '1.0'
    }

    if (format === 'json') {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `job-tracker-export-${new Date().toISOString().split('T')[0]}.json`
      a.click()
      URL.revokeObjectURL(url)
    } else if (format === 'csv') {
      // Export jobs as CSV
      const headers = ['Company', 'Position', 'Location', 'Salary', 'Status', 'Applied Date', 'Contact Person', 'Contact Email', 'Notes']
      const csvContent = [
        headers.join(','),
        ...jobs.map(job => [
          `"${job.company}"`,
          `"${job.position}"`,
          `"${job.location || ''}"`,
          `"${job.salary || ''}"`,
          `"${job.status}"`,
          `"${job.appliedDate || job.createdAt}"`,
          `"${job.contactPerson || ''}"`,
          `"${job.contactEmail || ''}"`,
          `"${job.notes || ''}"`
        ].join(','))
      ].join('\n')

      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `job-applications-${new Date().toISOString().split('T')[0]}.csv`
      a.click()
      URL.revokeObjectURL(url)
    }
  }

  const importData = (event) => {
    const file = event.target.files[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result)
        
        if (data.jobs && Array.isArray(data.jobs)) {
          // Clear existing data and import new data
          data.jobs.forEach(job => {
            addJob(job)
          })
        }
        
        if (data.documents && Array.isArray(data.documents)) {
          data.documents.forEach(doc => {
            addDocument(doc)
          })
        }
        
        setImportStatus('success')
        setImportMessage(`Successfully imported ${data.jobs?.length || 0} jobs and ${data.documents?.length || 0} documents`)
        
        setTimeout(() => {
          setImportStatus(null)
          setImportMessage('')
        }, 3000)
      } catch (error) {
        setImportStatus('error')
        setImportMessage('Invalid file format. Please upload a valid JSON file.')
        
        setTimeout(() => {
          setImportStatus(null)
          setImportMessage('')
        }, 3000)
      }
    }
    reader.readAsText(file)
  }

  return (
    <div className="card">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Data Management</h2>
      
      {/* Export Section */}
      <div className="mb-8">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Export Data</h3>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => exportData('json')}
            className="btn-primary inline-flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            Export as JSON
          </button>
          <button
            onClick={() => exportData('csv')}
            className="btn-secondary inline-flex items-center"
          >
            <FileText className="w-4 h-4 mr-2" />
            Export as CSV
          </button>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Export your job applications and documents for backup or migration.
        </p>
      </div>

      {/* Import Section */}
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Import Data</h3>
        <div className="flex items-center gap-3">
          <label className="btn-secondary inline-flex items-center cursor-pointer">
            <Upload className="w-4 h-4 mr-2" />
            Choose JSON File
            <input
              type="file"
              accept=".json"
              onChange={importData}
              className="hidden"
            />
          </label>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Import previously exported data. This will add to your existing data.
        </p>
      </div>

      {/* Status Messages */}
      {importStatus && (
        <div className={`p-4 rounded-lg flex items-center ${
          importStatus === 'success' 
            ? 'bg-green-50 text-green-800 border border-green-200' 
            : 'bg-red-50 text-red-800 border border-red-200'
        }`}>
          {importStatus === 'success' ? (
            <CheckCircle className="w-5 h-5 mr-2" />
          ) : (
            <AlertCircle className="w-5 h-5 mr-2" />
          )}
          {importMessage}
        </div>
      )}

      {/* Data Summary */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Data Summary</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Total Jobs</p>
            <p className="text-2xl font-bold text-gray-900">{jobs.length}</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Total Documents</p>
            <p className="text-2xl font-bold text-gray-900">{documents.length}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DataExport