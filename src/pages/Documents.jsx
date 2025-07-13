import React, { useState } from 'react'
import { useJobs } from '../contexts/JobContext'
import { 
  Plus, 
  FileText, 
  Download, 
  Edit, 
  Trash2, 
  Upload,
  Search,
  Filter
} from 'lucide-react'
import { format } from 'date-fns'

const Documents = () => {
  const { documents, addDocument, updateDocument, deleteDocument } = useJobs()
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [isAdding, setIsAdding] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    type: 'resume',
    description: '',
    fileUrl: '',
    tags: ''
  })

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.description?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = typeFilter === 'all' || doc.type === typeFilter
    return matchesSearch && matchesType
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    const documentData = {
      ...formData,
      tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
    }
    
    if (editingId) {
      updateDocument(editingId, documentData)
      setEditingId(null)
    } else {
      addDocument(documentData)
    }
    
    setFormData({
      name: '',
      type: 'resume',
      description: '',
      fileUrl: '',
      tags: ''
    })
    setIsAdding(false)
  }

  const handleEdit = (doc) => {
    setEditingId(doc.id)
    setFormData({
      name: doc.name,
      type: doc.type,
      description: doc.description || '',
      fileUrl: doc.fileUrl || '',
      tags: doc.tags?.join(', ') || ''
    })
    setIsAdding(true)
  }

  const handleCancel = () => {
    setIsAdding(false)
    setEditingId(null)
    setFormData({
      name: '',
      type: 'resume',
      description: '',
      fileUrl: '',
      tags: ''
    })
  }

  const handleDelete = (docId) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      deleteDocument(docId)
    }
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'resume': return <FileText className="w-5 h-5 text-blue-600" />
      case 'cover-letter': return <FileText className="w-5 h-5 text-green-600" />
      case 'portfolio': return <FileText className="w-5 h-5 text-purple-600" />
      case 'certificate': return <FileText className="w-5 h-5 text-yellow-600" />
      default: return <FileText className="w-5 h-5 text-gray-600" />
    }
  }

  const getTypeColor = (type) => {
    switch (type) {
      case 'resume': return 'bg-blue-100 text-blue-800'
      case 'cover-letter': return 'bg-green-100 text-green-800'
      case 'portfolio': return 'bg-purple-100 text-purple-800'
      case 'certificate': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
          <button
            onClick={() => setIsAdding(true)}
            className="btn-primary inline-flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Document
          </button>
        </div>
        <p className="text-gray-600">Manage your resumes, cover letters, and other job-related documents</p>
      </div>

      {/* Add/Edit Document Form */}
      {isAdding && (
        <div className="card mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            {editingId ? 'Edit Document' : 'Add New Document'}
          </h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Document Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  required
                  className="input-field"
                  placeholder="e.g., Software Engineer Resume v2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Document Type *
                </label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({...formData, type: e.target.value})}
                  className="input-field"
                >
                  <option value="resume">Resume</option>
                  <option value="cover-letter">Cover Letter</option>
                  <option value="portfolio">Portfolio</option>
                  <option value="certificate">Certificate</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                rows={3}
                className="input-field"
                placeholder="Brief description of the document..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                File URL or Path
              </label>
              <input
                type="text"
                value={formData.fileUrl}
                onChange={(e) => setFormData({...formData, fileUrl: e.target.value})}
                className="input-field"
                placeholder="Path to your document file or URL"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tags (comma-separated)
              </label>
              <input
                type="text"
                value={formData.tags}
                onChange={(e) => setFormData({...formData, tags: e.target.value})}
                className="input-field"
                placeholder="e.g., software engineer, react, frontend"
              />
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={handleCancel}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn-primary"
              >
                {editingId ? 'Update Document' : 'Add Document'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Filters */}
      <div className="card mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field pl-10"
            />
          </div>

          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="input-field"
          >
            <option value="all">All Types</option>
            <option value="resume">Resumes</option>
            <option value="cover-letter">Cover Letters</option>
            <option value="portfolio">Portfolios</option>
            <option value="certificate">Certificates</option>
            <option value="other">Other</option>
          </select>

          <div className="flex items-center text-sm text-gray-600">
            <Filter className="w-4 h-4 mr-2" />
            {filteredDocuments.length} of {documents.length} documents
          </div>
        </div>
      </div>

      {/* Documents Grid */}
      {filteredDocuments.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-gray-400 mb-4">
            <FileText className="w-16 h-16 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No documents found</h3>
          <p className="text-gray-600 mb-6">
            {documents.length === 0 
              ? "Get started by adding your first document"
              : "Try adjusting your search or filter criteria"
            }
          </p>
          {documents.length === 0 && (
            <button
              onClick={() => setIsAdding(true)}
              className="btn-primary inline-flex items-center"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add your first document
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDocuments.map((doc) => (
            <div key={doc.id} className="card hover:shadow-md transition-shadow duration-200">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  {getTypeIcon(doc.type)}
                  <div className="ml-3">
                    <h3 className="font-semibold text-gray-900">{doc.name}</h3>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium inline-block ${getTypeColor(doc.type)}`}>
                      {doc.type.replace('-', ' ')}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => handleEdit(doc)}
                    className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
                    title="Edit"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {doc.description && (
                <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                  {doc.description}
                </p>
              )}

              {doc.tags && doc.tags.length > 0 && (
                <div className="mb-4">
                  <div className="flex flex-wrap gap-1">
                    {doc.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>Created {format(new Date(doc.createdAt), 'MMM dd, yyyy')}</span>
                {doc.fileUrl && (
                  <a
                    href={doc.fileUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:text-primary-700 inline-flex items-center"
                  >
                    <Download className="w-3 h-3 mr-1" />
                    Open
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Documents