import React, { useState, useEffect } from 'react';
import { Activity, Server, Database, Clock, AlertTriangle, CheckCircle } from 'lucide-react';
import apiService from '../services/apiService';

const StatusDashboard = () => {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHealthData = async () => {
      try {
        const response = await apiService.get('/health');
        setHealthData(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch system health data');
        console.error('Health check failed:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchHealthData();
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchHealthData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
      case 'ok':
      case 'ready':
      case 'alive':
        return 'text-green-400';
      case 'degraded':
        return 'text-yellow-400';
      default:
        return 'text-red-400';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
      case 'ok':
      case 'ready':
      case 'alive':
        return <CheckCircle className="h-5 w-5 text-green-400" />;
      case 'degraded':
        return <AlertTriangle className="h-5 w-5 text-yellow-400" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-red-400" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-900 flex items-center justify-center">
        <div className="text-white">Loading system status...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-dark-900 flex items-center justify-center">
        <div className="text-red-400">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-900 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <Activity className="h-8 w-8 text-primary-500" />
          <h1 className="text-3xl font-bold text-white">System Status Dashboard</h1>
        </div>

        {/* Overall Status */}
        <div className="bg-dark-800 rounded-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {getStatusIcon(healthData?.status)}
              <div>
                <h2 className="text-xl font-semibold text-white">Overall System Status</h2>
                <p className={`text-lg ${getStatusColor(healthData?.status)}`}>
                  {healthData?.status?.toUpperCase() || 'UNKNOWN'}
                </p>
              </div>
            </div>
            <div className="text-right text-gray-400">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                <span>Last Updated: {new Date(healthData?.timestamp).toLocaleString()}</span>
              </div>
              <div className="text-sm mt-1">Version: {healthData?.version}</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Database Status */}
          <div className="bg-dark-800 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <Database className="h-6 w-6 text-blue-400" />
              <h3 className="text-lg font-semibold text-white">Database</h3>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Status:</span>
                <span className={getStatusColor(healthData?.database?.status)}>
                  {healthData?.database?.status}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Connection:</span>
                <span className={getStatusColor(healthData?.database?.connection)}>
                  {healthData?.database?.connection}
                </span>
              </div>
            </div>
          </div>

          {/* System Resources */}
          <div className="bg-dark-800 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <Server className="h-6 w-6 text-green-400" />
              <h3 className="text-lg font-semibold text-white">System Resources</h3>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">CPU Usage:</span>
                <span className="text-white">
                  {healthData?.system?.cpu_percent?.toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Memory Usage:</span>
                <span className="text-white">
                  {healthData?.system?.memory?.percent?.toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Disk Usage:</span>
                <span className="text-white">
                  {healthData?.system?.disk?.percent?.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>

          {/* Environment Variables */}
          <div className="bg-dark-800 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <AlertTriangle className="h-6 w-6 text-yellow-400" />
              <h3 className="text-lg font-semibold text-white">Environment</h3>
            </div>
            <div className="space-y-3">
              {healthData?.environment && Object.entries(healthData.environment).map(([key, value]) => (
                <div key={key} className="flex justify-between">
                  <span className="text-gray-400">{key}:</span>
                  <span className={value === 'set' ? 'text-green-400' : 'text-red-400'}>
                    {value}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Memory Details */}
          <div className="bg-dark-800 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <Activity className="h-6 w-6 text-purple-400" />
              <h3 className="text-lg font-semibold text-white">Memory Details</h3>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Total:</span>
                <span className="text-white">
                  {(healthData?.system?.memory?.total / 1024 / 1024 / 1024).toFixed(2)} GB
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Available:</span>
                <span className="text-white">
                  {(healthData?.system?.memory?.available / 1024 / 1024 / 1024).toFixed(2)} GB
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Raw Data (for debugging) */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mt-8 bg-dark-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Raw Health Data (Development Only)</h3>
            <pre className="text-sm text-gray-300 bg-dark-900 p-4 rounded overflow-auto">
              {JSON.stringify(healthData, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default StatusDashboard;
