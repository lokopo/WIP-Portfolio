import React, { createContext, useContext, useReducer, useEffect } from 'react'

const JobContext = createContext()

const initialState = {
  jobs: [],
  documents: [],
  loading: false,
  error: null
}

const jobReducer = (state, action) => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload }
    case 'SET_ERROR':
      return { ...state, error: action.payload }
    case 'LOAD_JOBS':
      return { ...state, jobs: action.payload }
    case 'ADD_JOB':
      return { ...state, jobs: [...state.jobs, action.payload] }
    case 'UPDATE_JOB':
      return {
        ...state,
        jobs: state.jobs.map(job => 
          job.id === action.payload.id ? action.payload : job
        )
      }
    case 'DELETE_JOB':
      return {
        ...state,
        jobs: state.jobs.filter(job => job.id !== action.payload)
      }
    case 'LOAD_DOCUMENTS':
      return { ...state, documents: action.payload }
    case 'ADD_DOCUMENT':
      return { ...state, documents: [...state.documents, action.payload] }
    case 'UPDATE_DOCUMENT':
      return {
        ...state,
        documents: state.documents.map(doc => 
          doc.id === action.payload.id ? action.payload : doc
        )
      }
    case 'DELETE_DOCUMENT':
      return {
        ...state,
        documents: state.documents.filter(doc => doc.id !== action.payload)
      }
    default:
      return state
  }
}

export const JobProvider = ({ children }) => {
  const [state, dispatch] = useReducer(jobReducer, initialState)

  // Load data from localStorage on mount
  useEffect(() => {
    const loadData = () => {
      try {
        const savedJobs = localStorage.getItem('jobApplications')
        const savedDocuments = localStorage.getItem('jobDocuments')
        
        if (savedJobs) {
          dispatch({ type: 'LOAD_JOBS', payload: JSON.parse(savedJobs) })
        }
        if (savedDocuments) {
          dispatch({ type: 'LOAD_DOCUMENTS', payload: JSON.parse(savedDocuments) })
        }
      } catch (error) {
        dispatch({ type: 'SET_ERROR', payload: 'Failed to load saved data' })
      }
    }
    
    loadData()
  }, [])

  // Save data to localStorage whenever state changes
  useEffect(() => {
    localStorage.setItem('jobApplications', JSON.stringify(state.jobs))
  }, [state.jobs])

  useEffect(() => {
    localStorage.setItem('jobDocuments', JSON.stringify(state.documents))
  }, [state.documents])

  const addJob = (jobData) => {
    const newJob = {
      id: Date.now().toString(),
      createdAt: new Date().toISOString(),
      status: 'applied',
      ...jobData
    }
    dispatch({ type: 'ADD_JOB', payload: newJob })
  }

  const updateJob = (jobId, updates) => {
    const job = state.jobs.find(j => j.id === jobId)
    if (job) {
      const updatedJob = { ...job, ...updates, updatedAt: new Date().toISOString() }
      dispatch({ type: 'UPDATE_JOB', payload: updatedJob })
    }
  }

  const deleteJob = (jobId) => {
    dispatch({ type: 'DELETE_JOB', payload: jobId })
  }

  const addDocument = (documentData) => {
    const newDocument = {
      id: Date.now().toString(),
      createdAt: new Date().toISOString(),
      ...documentData
    }
    dispatch({ type: 'ADD_DOCUMENT', payload: newDocument })
  }

  const updateDocument = (documentId, updates) => {
    const document = state.documents.find(d => d.id === documentId)
    if (document) {
      const updatedDocument = { ...document, ...updates, updatedAt: new Date().toISOString() }
      dispatch({ type: 'UPDATE_DOCUMENT', payload: updatedDocument })
    }
  }

  const deleteDocument = (documentId) => {
    dispatch({ type: 'DELETE_DOCUMENT', payload: documentId })
  }

  const value = {
    ...state,
    addJob,
    updateJob,
    deleteJob,
    addDocument,
    updateDocument,
    deleteDocument
  }

  return (
    <JobContext.Provider value={value}>
      {children}
    </JobContext.Provider>
  )
}

export const useJobs = () => {
  const context = useContext(JobContext)
  if (!context) {
    throw new Error('useJobs must be used within a JobProvider')
  }
  return context
}