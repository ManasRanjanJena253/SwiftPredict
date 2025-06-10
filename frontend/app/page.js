'use client';
import React, { useState, useEffect } from 'react';
import { ChevronRight, Database, Brain, Activity, Send, Download, Upload, Settings, Home, Menu, X, FileText, BarChart3, Trash2 } from 'lucide-react';

const SwiftPredictUI = () => {
  const [activeTab, setActiveTab] = useState('home');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [apiResponse, setApiResponse] = useState('');
  const [selectedEndpoint, setSelectedEndpoint] = useState(null);
  const [formData, setFormData] = useState({});
  const [projects, setProjects] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);

  // API base URL - adjust this to your FastAPI server
  const API_BASE = 'http://localhost:9000';

  // Define your API endpoints based on your FastAPI code
  const automlApis = [
    {
      path: '/automl/train',
      method: 'POST',
      summary: 'Train AutoML Model',
      description: 'Upload CSV file and train AutoML models',
      tags: ['automl'],
      requiresFile: true,
      parameters: ['project_name', 'target_column']
    },
    {
      path: '/automl/predict',
      method: 'GET',
      summary: 'Make Predictions',
      description: 'Get predictions from trained model',
      tags: ['automl'],
      parameters: ['data']
    }
  ];

  const loggerApis = [
    {
      path: '/{project_name}/runs/{run_id}/log_param',
      method: 'POST',
      summary: 'Log Parameter',
      description: 'Log parameters used when training a model',
      tags: ['logger'],
      parameters: ['key', 'value', 'run_id', 'project_name']
    },
    {
      path: '/{project_name}/runs/{run_id}/log_metric',
      method: 'POST',
      summary: 'Log Metric',
      description: 'Log metrics for model evaluation',
      tags: ['logger'],
      parameters: ['key', 'value', 'step', 'run_id', 'project_name']
    },
    {
      path: '/{project_name}/runs/{run_id}/add_tags',
      method: 'POST',
      summary: 'Add Tags',
      description: 'Add tags to existing runs',
      tags: ['logger'],
      parameters: ['run_id', 'project_name', 'tags']
    },
    {
      path: '/{project_name}/runs/{run_id}/update_status',
      method: 'POST',
      summary: 'Update Status',
      description: 'Update the running status of a project',
      tags: ['logger'],
      parameters: ['run_id', 'project_name', 'status']
    },
    {
      path: '/{project_name}/runs/{run_id}/add_notes',
      method: 'POST',
      summary: 'Add Notes',
      description: 'Add notes for experiment description',
      tags: ['logger'],
      parameters: ['run_id', 'project_name', 'notes']
    },
    {
      path: '/projects/{status}',
      method: 'GET',
      summary: 'Get Projects by Status',
      description: 'Get all projects with specific status',
      tags: ['logger'],
      parameters: ['status']
    },
    {
      path: '/{project_name}/runs/{run_id}',
      method: 'GET',
      summary: 'Fetch Run Details',
      description: 'Fetch all data for a specific run_id',
      tags: ['logger'],
      parameters: ['run_id', 'project_name']
    },
    {
      path: '/projects',
      method: 'GET',
      summary: 'Get All Projects',
      description: 'Get all distinct projects',
      tags: ['logger']
    },
    {
      path: '/{project_name}/plots/available_metrics',
      method: 'GET',
      summary: 'Available Metrics',
      description: 'Get all available metrics for a project',
      tags: ['logger'],
      parameters: ['project_name']
    },
    {
      path: '/{project_name}/plots/{metric}',
      method: 'GET',
      summary: 'Plot Metrics',
      description: 'Generate metric plots for visualization',
      tags: ['logger'],
      parameters: ['metric', 'run_id', 'project_name']
    },
    {
      path: '/projects/delete',
      method: 'DELETE',
      summary: 'Delete Projects',
      description: 'Delete projects by name or run_id',
      tags: ['logger'],
      parameters: ['project_name', 'run_id']
    },
    {
      path: '/delete_all',
      method: 'DELETE',
      summary: 'Delete All Records',
      description: 'Delete all records of all projects',
      tags: ['logger']
    }
  ];

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await fetch(`${API_BASE}/projects`);
      const data = await response.json();
      setProjects(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
      setProjects([]);
    }
  };

  const executeApi = async (endpoint) => {
    try {
      setLoading(true);
      let url = `${API_BASE}${endpoint.path}`;

      // Replace path parameters with actual values
      if (formData.project_name) {
        url = url.replace('{project_name}', formData.project_name);
      }
      if (formData.run_id) {
        url = url.replace('{run_id}', formData.run_id);
      }
      if (formData.status) {
        url = url.replace('{status}', formData.status);
      }
      if (formData.metric) {
        url = url.replace('{metric}', formData.metric);
      }

      const options = {
        method: endpoint.method,
        headers: {}
      };

      if (endpoint.requiresFile && selectedFile) {
        const formDataObj = new FormData();
        formDataObj.append('file', selectedFile);
        if (formData.project_name) formDataObj.append('project_name', formData.project_name);
        if (formData.target_column) formDataObj.append('target_column', formData.target_column);
        options.body = formDataObj;
      } else if (endpoint.method !== 'GET' && Object.keys(formData).length > 0) {
        options.headers['Content-Type'] = 'application/json';

        // For POST requests, send as query parameters for your API structure
        const queryParams = new URLSearchParams();
        Object.entries(formData).forEach(([key, value]) => {
          if (value && !['project_name', 'run_id', 'status', 'metric'].includes(key)) {
            if (Array.isArray(value)) {
              queryParams.append(key, JSON.stringify(value));
            } else {
              queryParams.append(key, value);
            }
          }
        });

        if (queryParams.toString()) {
          url += (url.includes('?') ? '&' : '?') + queryParams.toString();
        }
      } else if (endpoint.method === 'GET' && Object.keys(formData).length > 0) {
        const queryParams = new URLSearchParams();
        Object.entries(formData).forEach(([key, value]) => {
          if (value && !['project_name', 'run_id', 'status', 'metric'].includes(key)) {
            queryParams.append(key, value);
          }
        });

        if (queryParams.toString()) {
          url += (url.includes('?') ? '&' : '?') + queryParams.toString();
        }
      }

      const response = await fetch(url, options);

      // Handle image responses (for plot endpoints)
      if (response.headers.get('content-type')?.includes('image')) {
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);
        setApiResponse(`Image URL: ${imageUrl}\n\n[Image will be displayed in browser]`);
        // Open image in new tab
        window.open(imageUrl, '_blank');
      } else {
        const data = await response.json();
        setApiResponse(JSON.stringify(data, null, 2));
      }
    } catch (error) {
      setApiResponse(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const Sidebar = () => (
    <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-gradient-to-b from-amber-900 to-amber-800 shadow-xl transform transition-transform duration-300 ease-in-out ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 lg:static lg:inset-0`}>
      <div className="flex items-center justify-between h-16 px-6 border-b border-amber-700/30">
        <h1 className="text-xl font-bold text-amber-100">SwiftPredict</h1>
        <button
          onClick={() => setSidebarOpen(false)}
          className="lg:hidden text-amber-200 hover:text-white transition-colors"
        >
          <X size={20} />
        </button>
      </div>

      <nav className="mt-8">
        {[
          { id: 'home', label: 'Dashboard', icon: Home },
          { id: 'automl', label: 'AutoML APIs', icon: Brain },
          { id: 'logger', label: 'Logger APIs', icon: Activity },
          { id: 'settings', label: 'Settings', icon: Settings }
        ].map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => {
              setActiveTab(id);
              setSidebarOpen(false);
            }}
            className={`w-full flex items-center px-6 py-3 text-left transition-all duration-200 hover:bg-amber-700/30 ${
              activeTab === id ? 'bg-amber-700/40 border-r-2 border-yellow-500 text-white font-medium' : 'text-amber-100 hover:text-white'
            }`}
          >
            <Icon size={20} className="mr-3" />
            {label}
          </button>
        ))}
      </nav>
    </div>
  );

  const ApiCard = ({ endpoint, type }) => (
    <div className="bg-amber-50 rounded-lg p-6 border border-amber-200 hover:border-yellow-600 transition-all duration-300 hover:shadow-lg shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
            endpoint.method === 'GET' ? 'bg-green-100 text-green-800' :
            endpoint.method === 'POST' ? 'bg-amber-100 text-amber-800' :
            endpoint.method === 'DELETE' ? 'bg-red-100 text-red-800' :
            'bg-yellow-100 text-yellow-800'
          }`}>
            {endpoint.method}
          </span>
          <code className="text-amber-900 font-mono text-sm bg-amber-100 px-2 py-1 rounded">
            {endpoint.path}
          </code>
        </div>
        <ChevronRight className="text-yellow-700" size={16} />
      </div>

      <h3 className="text-amber-900 font-semibold mb-2">{endpoint.summary}</h3>
      <p className="text-amber-700 text-sm mb-4">{endpoint.description}</p>

      <div className="flex space-x-2">
        <button
          onClick={() => {
            setSelectedEndpoint(endpoint);
            setFormData({});
            setSelectedFile(null);
          }}
          className="flex items-center px-4 py-2 bg-amber-700 hover:bg-amber-800 text-white rounded-lg transition-colors duration-200 text-sm"
          style={{ backgroundColor: '#996515' }}
        >
          <Send size={14} className="mr-2" />
          Test API
        </button>
        {endpoint.method === 'GET' && (
          <button
            onClick={() => executeApi(endpoint)}
            className="flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors duration-200 text-sm"
          >
            <Download size={14} className="mr-2" />
            Fetch
          </button>
        )}
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'home':
        return (
          <div className="space-y-8">
            <div className="text-center py-12">
              <div className="mb-6">
                <Database className="mx-auto text-yellow-700" size={64} style={{ color: '#996515' }} />
              </div>
              <h1 className="text-4xl font-bold text-amber-900 mb-4">
                SwiftPredict
              </h1>
              <p className="text-xl text-amber-700 mb-8 max-w-2xl mx-auto">
                Your compass from data to discovery. Explore powerful AutoML capabilities and comprehensive logging solutions.
              </p>
              <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                <div className="bg-gradient-to-br from-amber-50 to-amber-100 p-8 rounded-xl border border-amber-200">
                  <Brain className="text-amber-700 mb-4" size={48} style={{ color: '#996515' }} />
                  <h3 className="text-xl font-semibold text-amber-900 mb-2">AutoML APIs</h3>
                  <p className="text-amber-700 mb-4">Train, predict, and manage machine learning models with ease.</p>
                  <span className="text-yellow-700 font-medium" style={{ color: '#CCAA00' }}>{automlApis.length} endpoints available</span>
                </div>
                <div className="bg-gradient-to-br from-green-50 to-green-100 p-8 rounded-xl border border-green-200">
                  <Activity className="text-green-600 mb-4" size={48} />
                  <h3 className="text-xl font-semibold text-amber-900 mb-2">Logger APIs</h3>
                  <p className="text-amber-700 mb-4">Monitor, track, and analyze your system activities.</p>
                  <span className="text-green-700 font-medium">{loggerApis.length} endpoints available</span>
                </div>
              </div>

              {projects.length > 0 && (
                <div className="mt-12">
                  <h2 className="text-2xl font-bold text-amber-900 mb-4">Your Projects</h2>
                  <div className="flex flex-wrap gap-2 justify-center">
                    {projects.map((project, index) => (
                      <span key={index} className="px-3 py-1 bg-amber-100 text-amber-800 rounded-full text-sm">
                        {project}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        );

      case 'automl':
        return (
          <div>
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-amber-900 mb-2">AutoML APIs</h2>
              <p className="text-amber-700">Manage your machine learning workflows</p>
            </div>

            <div className="grid gap-6">
              {automlApis.map((endpoint, index) => (
                <ApiCard key={index} endpoint={endpoint} type="automl" />
              ))}
            </div>
          </div>
        );

      case 'logger':
        return (
          <div>
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-amber-900 mb-2">Logger APIs</h2>
              <p className="text-amber-700">Monitor and manage system logs</p>
            </div>

            <div className="grid gap-6">
              {loggerApis.map((endpoint, index) => (
                <ApiCard key={index} endpoint={endpoint} type="logger" />
              ))}
            </div>
          </div>
        );

      case 'settings':
        return (
          <div>
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-amber-900 mb-2">Settings</h2>
              <p className="text-amber-700">Configure your SwiftPredict environment</p>
            </div>

            <div className="bg-amber-50 rounded-lg p-6 border border-amber-200 shadow-sm">
              <h3 className="text-amber-900 font-semibold mb-4">API Configuration</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-amber-800 text-sm font-medium mb-2">
                    Base URL
                  </label>
                  <input
                    type="text"
                    value={API_BASE}
                    className="w-full px-4 py-2 bg-amber-100 border border-amber-300 rounded-lg text-amber-900 focus:border-yellow-600 focus:outline-none focus:ring-2 focus:ring-yellow-200"
                    placeholder="http://localhost:9000"
                    style={{ backgroundColor: '#E8D6B9' }}
                  />
                </div>
                <button
                  className="px-6 py-2 bg-amber-700 hover:bg-amber-800 text-white rounded-lg transition-colors duration-200"
                  style={{ backgroundColor: '#996515' }}
                >
                  Save Configuration
                </button>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="flex h-screen" style={{ backgroundColor: '#F5E6CC' }}>
      {/* Sidebar - Hidden on mobile, always visible on desktop */}
      <div className="hidden lg:block">
        <Sidebar />
      </div>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <>
          <div
            className="lg:hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            onClick={() => setSidebarOpen(false)}
          />
          <div className="lg:hidden">
            <Sidebar />
          </div>
        </>
      )}

      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <button
          onClick={() => setSidebarOpen(true)}
          className="p-2 text-white rounded-lg shadow-lg"
          style={{ backgroundColor: '#996515' }}
        >
          <Menu size={20} />
        </button>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-h-0">
        <main className="flex-1 p-6 lg:p-8 overflow-y-auto">
          {renderContent()}
        </main>
      </div>

      {/* API Test Modal */}
      {selectedEndpoint && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-amber-50 rounded-xl p-6 border border-amber-200 max-w-2xl w-full max-h-[80vh] overflow-y-auto shadow-xl" style={{ backgroundColor: '#E8D6B9' }}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-amber-900">
                Test API: {selectedEndpoint.path}
              </h3>
              <button
                onClick={() => setSelectedEndpoint(null)}
                className="text-amber-600 hover:text-amber-800 transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            {selectedEndpoint.requiresFile && (
              <div className="mb-4">
                <label className="block text-amber-800 text-sm font-medium mb-2">
                  Upload CSV File
                </label>
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => setSelectedFile(e.target.files[0])}
                  className="w-full px-4 py-2 bg-amber-100 border border-amber-300 rounded-lg text-amber-900 focus:border-yellow-600 focus:outline-none"
                />
              </div>
            )}

            {selectedEndpoint.parameters && (
              <div className="mb-4 space-y-3">
                <label className="block text-amber-800 text-sm font-medium mb-2">
                  Parameters
                </label>
                {selectedEndpoint.parameters.map((param) => (
                  <div key={param}>
                    <label className="block text-amber-700 text-xs mb-1">{param}</label>
                    {param === 'tags' ? (
                      <input
                        type="text"
                        placeholder="Enter comma-separated tags"
                        value={formData[param] || ''}
                        onChange={(e) => {
                          const tags = e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag);
                          setFormData({...formData, [param]: tags});
                        }}
                        className="w-full px-3 py-2 bg-amber-100 border border-amber-300 rounded text-amber-900 focus:border-yellow-600 focus:outline-none text-sm"
                      />
                    ) : param === 'notes' ? (
                      <textarea
                        placeholder={`Enter ${param}`}
                        value={formData[param] || ''}
                        onChange={(e) => setFormData({...formData, [param]: e.target.value})}
                        className="w-full px-3 py-2 bg-amber-100 border border-amber-300 rounded text-amber-900 focus:border-yellow-600 focus:outline-none text-sm h-20"
                      />
                    ) : (
                      <input
                        type={param === 'step' || param === 'value' ? 'number' : 'text'}
                        placeholder={`Enter ${param}`}
                        value={formData[param] || ''}
                        onChange={(e) => setFormData({...formData, [param]: e.target.value})}
                        className="w-full px-3 py-2 bg-amber-100 border border-amber-300 rounded text-amber-900 focus:border-yellow-600 focus:outline-none text-sm"
                      />
                    )}
                  </div>
                ))}
              </div>
            )}

            <div className="flex space-x-3 mb-4">
              <button
                onClick={() => executeApi(selectedEndpoint)}
                disabled={loading}
                className="flex items-center px-4 py-2 hover:bg-amber-800 disabled:bg-amber-400 text-white rounded-lg transition-colors duration-200"
                style={{ backgroundColor: loading ? '#996515' : '#996515' }}
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                ) : (
                  <Send size={16} className="mr-2" />
                )}
                Execute
              </button>
            </div>

            {apiResponse && (
              <div>
                <label className="block text-amber-800 text-sm font-medium mb-2">
                  Response
                </label>
                <pre className="w-full h-64 px-4 py-2 bg-amber-100 border border-amber-300 rounded-lg text-amber-900 overflow-auto font-mono text-sm">
                  {apiResponse}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SwiftPredictUI;