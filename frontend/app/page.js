import React, { useState, useEffect } from 'react';
import { Search, Database, Activity, BarChart3, Settings, Play, Trash2, Eye, Tag, FileText, ChevronDown, ChevronRight, X } from 'lucide-react';

const SwiftPredictUI = () => {
  const [activeEndpoint, setActiveEndpoint] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [formData, setFormData] = useState({});
  const [showModal, setShowModal] = useState(false);
  const [projects, setProjects] = useState([]);
  const [error, setError] = useState('');

  const API_BASE = 'http://localhost:8000';

  const endpoints = [
    { id: 'dashboard', name: 'Dashboard', icon: Database, method: 'GET' },
    { id: 'log_param', name: 'Log Parameter', icon: Settings, method: 'POST', params: ['project_name', 'run_id', 'key', 'value'] },
    { id: 'log_metric', name: 'Log Metric', icon: Activity, method: 'POST', params: ['project_name', 'run_id', 'key', 'value', 'step'] },
    { id: 'add_tags', name: 'Add Tags', icon: Tag, method: 'POST', params: ['project_name', 'run_id', 'tags'] },
    { id: 'update_status', name: 'Update Status', icon: Play, method: 'POST', params: ['project_name', 'run_id', 'status'] },
    { id: 'add_notes', name: 'Add Notes', icon: FileText, method: 'POST', params: ['project_name', 'run_id', 'notes'] },
    { id: 'projects_by_status', name: 'Projects by Status', icon: Search, method: 'GET', params: ['status'] },
    { id: 'fetch_run', name: 'Fetch Run', icon: Eye, method: 'GET', params: ['project_name', 'run_id'] },
    { id: 'dl_projects', name: 'DL Projects', icon: BarChart3, method: 'GET' },
    { id: 'ml_projects', name: 'ML Projects', icon: BarChart3, method: 'GET' },
    { id: 'available_metrics', name: 'Available Metrics', icon: BarChart3, method: 'GET', params: ['project_name'] },
    { id: 'plot_metrics', name: 'Plot Metrics', icon: BarChart3, method: 'GET', params: ['project_name', 'run_id', 'metric'] },
    { id: 'delete_projects', name: 'Delete Projects', icon: Trash2, method: 'DELETE', params: ['project_name', 'run_id'] }
  ];

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [dlResponse, mlResponse] = await Promise.all([
        fetch(`${API_BASE}/projects/dl`),
        fetch(`${API_BASE}/projects/ml`)
      ]);

      const dlData = await dlResponse.json();
      const mlData = await mlResponse.json();

      const combinedData = [
        ...(Array.isArray(dlData) ? dlData.map(p => ({ ...p, type: 'Deep Learning' })) : []),
        ...(Array.isArray(mlData) ? mlData.map(p => ({ ...p, type: 'Machine Learning' })) : [])
      ];

      setData(combinedData);
      setProjects([...new Set(combinedData.map(p => p.project_name))]);
    } catch (error) {
      setError('Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const executeEndpoint = async (endpoint) => {
    try {
      setLoading(true);
      setError('');

      let url = `${API_BASE}`;

      switch (endpoint.id) {
        case 'log_param':
          url += `/${formData.project_name}/runs/${formData.run_id}/log_param?key=${formData.key}&value=${formData.value}`;
          break;
        case 'log_metric':
          url += `/${formData.project_name}/runs/${formData.run_id}/log_metric?key=${formData.key}&value=${formData.value}&step=${formData.step}`;
          break;
        case 'add_tags':
          url += `/${formData.project_name}/runs/${formData.run_id}/add_tags`;
          break;
        case 'update_status':
          url += `/${formData.project_name}/runs/${formData.run_id}/update_status?status=${formData.status}`;
          break;
        case 'add_notes':
          url += `/${formData.project_name}/runs/${formData.run_id}/add_notes`;
          break;
        case 'projects_by_status':
          url += `/projects/${formData.status}`;
          break;
        case 'fetch_run':
          url += `/${formData.project_name}/runs/${formData.run_id}`;
          break;
        case 'dl_projects':
          url += '/projects/dl';
          break;
        case 'ml_projects':
          url += '/projects/ml';
          break;
        case 'available_metrics':
          url += `/${formData.project_name}/plots/available_metrics`;
          break;
        case 'plot_metrics':
          url += `/${formData.project_name}/plots/${formData.metric}?run_id=${formData.run_id}`;
          break;
        case 'delete_projects':
          url += `/projects/delete?project_name=${formData.project_name}${formData.run_id ? `&run_id=${formData.run_id}` : ''}`;
          break;
        default:
          return;
      }

      const options = {
        method: endpoint.method,
        headers: { 'Content-Type': 'application/json' }
      };

      if (endpoint.method === 'POST' && ['add_tags', 'add_notes'].includes(endpoint.id)) {
        options.body = JSON.stringify(
          endpoint.id === 'add_tags'
            ? { tags: formData.tags.split(',').map(t => t.trim()) }
            : { notes: formData.notes }
        );
      }

      const response = await fetch(url, options);

      if (response.headers.get('content-type')?.includes('image')) {
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);
        window.open(imageUrl, '_blank');
        setData([{ message: 'Chart opened in new tab' }]);
      } else {
        const result = await response.json();

        if (Array.isArray(result)) {
          setData(result.map(item => ({ ...item, type: endpoint.id.includes('dl') ? 'Deep Learning' : 'Machine Learning' })));
        } else if (result.data && Array.isArray(result.data)) {
          setData(result.data);
        } else if (result.all_available_metrics && Array.isArray(result.all_available_metrics)) {
          setData(result.all_available_metrics);
        } else {
          setData([result]);
        }
      }

      setShowModal(false);
      setFormData({});

      if (endpoint.method !== 'GET') {
        fetchDashboardData();
      }
    } catch (error) {
      setError(`Error: ${error.message}`);
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  const openModal = (endpoint) => {
    setActiveEndpoint(endpoint.id);
    setFormData({});
    setShowModal(true);
  };

  const renderTable = () => {
    if (!data.length) return <div className="text-center text-slate-500 py-8">No data available</div>;

    const firstItem = data[0];
    const columns = Object.keys(firstItem).filter(key => !['_id', '__v'].includes(key));

    return (
      <div className="overflow-x-auto bg-white rounded-lg shadow-sm border border-slate-200">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              {columns.map(column => (
                <th key={column} className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  {column.replace(/_/g, ' ')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-slate-200">
            {data.map((item, index) => (
              <tr key={index} className="hover:bg-slate-50">
                {columns.map(column => (
                  <td key={column} className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                    {typeof item[column] === 'object'
                      ? JSON.stringify(item[column])
                      : item[column]?.toString() || '-'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderForm = (endpoint) => {
    if (!endpoint.params) return null;

    return (
      <div className="space-y-4">
        {endpoint.params.map(param => (
          <div key={param}>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              {param.replace(/_/g, ' ').toUpperCase()}
            </label>
            {param === 'status' ? (
              <select
                value={formData[param] || ''}
                onChange={(e) => setFormData({...formData, [param]: e.target.value})}
                className="input-field"
              >
                <option value="">Select status</option>
                <option value="running">Running</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
                <option value="paused">Paused</option>
              </select>
            ) : param === 'project_name' && projects.length > 0 ? (
              <select
                value={formData[param] || ''}
                onChange={(e) => setFormData({...formData, [param]: e.target.value})}
                className="input-field"
              >
                <option value="">Select project</option>
                {projects.map(project => (
                  <option key={project} value={project}>{project}</option>
                ))}
              </select>
            ) : param === 'notes' ? (
              <textarea
                value={formData[param] || ''}
                onChange={(e) => setFormData({...formData, [param]: e.target.value})}
                className="input-field h-20"
                placeholder={`Enter ${param.replace(/_/g, ' ')}`}
              />
            ) : (
              <input
                type={['value', 'step'].includes(param) ? 'number' : 'text'}
                value={formData[param] || ''}
                onChange={(e) => setFormData({...formData, [param]: e.target.value})}
                className="input-field"
                placeholder={`Enter ${param.replace(/_/g, ' ')}`}
              />
            )}
          </div>
        ))}
      </div>
    );
  };

  const currentEndpoint = endpoints.find(e => e.id === activeEndpoint);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <style jsx>{`
        .input-field {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #e2e8f0;
          border-radius: 0.5rem;
          background: white;
          color: #1e293b;
          font-size: 0.875rem;
          transition: border-color 0.2s;
        }
        .input-field:focus {
          outline: none;
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        .btn-primary {
          background: linear-gradient(135deg, #3b82f6, #1d4ed8);
          color: white;
          padding: 0.75rem 1.5rem;
          border-radius: 0.5rem;
          font-weight: 500;
          transition: all 0.2s;
          border: none;
          cursor: pointer;
        }
        .btn-primary:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }
        .btn-secondary {
          background: white;
          color: #475569;
          padding: 0.75rem 1.5rem;
          border: 1px solid #e2e8f0;
          border-radius: 0.5rem;
          font-weight: 500;
          transition: all 0.2s;
          cursor: pointer;
        }
        .btn-secondary:hover {
          background: #f8fafc;
          border-color: #cbd5e1;
        }
      `}</style>

      {/* Header */}
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Database className="h-8 w-8 text-blue-600" />
              <h1 className="text-xl font-bold text-slate-900">SwiftPredict</h1>
            </div>
            <nav className="hidden md:flex space-x-1">
              {endpoints.map(endpoint => (
                <button
                  key={endpoint.id}
                  onClick={() => {
                    if (endpoint.method === 'GET' && !endpoint.params) {
                      setActiveEndpoint(endpoint.id);
                      executeEndpoint(endpoint);
                    } else {
                      openModal(endpoint);
                    }
                  }}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeEndpoint === endpoint.id
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <endpoint.icon className="h-4 w-4 mr-2" />
                  {endpoint.name}
                </button>
              ))}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-slate-900 mb-2">
            {currentEndpoint?.name || 'Dashboard'}
          </h2>
          <p className="text-slate-600 text-sm">
            {activeEndpoint === 'dashboard'
              ? 'Overview of your machine learning experiments'
              : `${currentEndpoint?.method} endpoint results`}
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          renderTable()
        )}
      </main>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-slate-900">
                {currentEndpoint?.name}
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {renderForm(currentEndpoint)}

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowModal(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() => executeEndpoint(currentEndpoint)}
                disabled={loading}
                className="btn-primary"
              >
                {loading ? 'Processing...' : 'Execute'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SwiftPredictUI;