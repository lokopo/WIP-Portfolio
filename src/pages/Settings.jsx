import React from 'react'
import DataExport from '../components/DataExport'
import AnalyticsChart from '../components/AnalyticsChart'

const Settings = () => {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
        <p className="text-gray-600">Manage your application data and preferences</p>
      </div>

      <div className="max-w-6xl space-y-8">
        <DataExport />
        <AnalyticsChart />
      </div>
    </div>
  )
}

export default Settings