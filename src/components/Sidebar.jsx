import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  Home, 
  Briefcase, 
  FileText, 
  Plus,
  BarChart3
} from 'lucide-react'

const Sidebar = () => {
  const location = useLocation()

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/jobs', icon: Briefcase, label: 'Job Applications' },
    { path: '/jobs/add', icon: Plus, label: 'Add Job' },
    { path: '/documents', icon: FileText, label: 'Documents' },
  ]

  return (
    <div className="w-64 bg-white shadow-lg border-r border-gray-200">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-primary-600">Job Tracker</h1>
        <p className="text-gray-600 text-sm mt-1">Manage your applications</p>
      </div>
      
      <nav className="mt-6">
        <ul className="space-y-2 px-4">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`flex items-center px-4 py-3 rounded-lg transition-colors duration-200 ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-600'
                      : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Icon className="w-5 h-5 mr-3" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>
      
      <div className="absolute bottom-6 left-6 right-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center">
            <BarChart3 className="w-5 h-5 text-gray-600 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-900">Job Tracker Pro</p>
              <p className="text-xs text-gray-600">Stay organized</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Sidebar