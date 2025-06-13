'use client';

import { useState, useEffect } from 'react';

const API_BASE = 'http://127.0.0.1:8000';

export default function SwiftPredictUI() {
  const [activeTab, setActiveTab] = useState('view');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // View Data State
  const [projects, setProjects] = useState({ ml: [], dl: [] });
  const [selectedProject, setSelectedProject] = useState('');
  const [runDetails, setRunDetails] = useState([]);
  const [availableMetrics, setAvailableMetrics] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [statusProjects, setStatusProjects] = useState([]);

  // Log Data State
  const [logForm, setLogForm] = useState({
    projectName: '',
    runId: '',
    action: 'log_param',
    key: '',
    value: '',
    tags: '',
    status: '',
    notes: '',
    metric: ''
  });

  // Fetch projects on component mount
  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const [mlResponse, dlResponse] = await Promise.all([
        fetch(`${API_BASE}/projects/ml`),
        fetch(`${API_BASE}/projects/dl`)
      ]);

      const mlData = await mlResponse.json();
      const dlData = await dlResponse.json();

      setProjects({
        ml: Array.isArray(mlData) ? mlData : [],
        dl: Array.isArray(dlData) ? dlData : []
      });
    } catch (err) {
      setError('Failed to fetch projects');
    } finally {
      setLoading(false);
    }
  };

  const fetchRunDetails = async (projectName, runId) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/${projectName}/runs/${runId}`);
      const data = await response.json();
      setRunDetails(Array.isArray(data) ? data : []);
    } catch (err) {
      setError('Failed to fetch run details');
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableMetrics = async (projectName) => {
    try {
      const response = await fetch(`${API_BASE}/${projectName}/plots/available_metrics`);
      const data = await response.json();
      setAvailableMetrics(data.all_available_metrics || []);
    } catch (err) {
      setError('Failed to fetch metrics');
    }
  };

  const fetchProjectsByStatus = async (status) => {
    if (!status) return;
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/projects/${status}`);
      const data = await response.json();
      setStatusProjects(data.data || []);
    } catch (err) {
      setError('Failed to fetch projects by status');
    } finally {
      setLoading(false);
    }
  };

  const handleLogSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      let url = '';
      let body = {};

      switch (logForm.action) {
        case 'log_param':
          url = `${API_BASE}/${logForm.projectName}/runs/${logForm.runId}/log_param?key=${logForm.key}&value=${logForm.value}`;
          break;
        case 'add_tags':
          url = `${API_BASE}/${logForm.projectName}/runs/${logForm.runId}/add_tags`;
          body = { tags: logForm.tags.split(',').map(tag => tag.trim()) };
          break;
        case 'update_status':
          url = `${API_BASE}/${logForm.projectName}/runs/${logForm.runId}/update_status?status=${logForm.status}`;
          break;
        case 'add_notes':
          url = `${API_BASE}/${logForm.projectName}/runs/${logForm.runId}/add_notes?notes=${logForm.notes}`;
          break;
      }

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: Object.keys(body).length ? JSON.stringify(body) : undefined
      });

      const data = await response.json();
      
      if (data.Error) {
        setError(data.Error);
      } else {
        setSuccess('Action completed successfully!');
        setLogForm({
          projectName: '',
          runId: '',
          action: 'log_param',
          key: '',
          value: '',
          tags: '',
          status: '',
          notes: '',
          metric: ''
        });
      }
    } catch (err) {
      setError('Failed to submit log data');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProject = async (projectName, runId = '') => {
    if (!confirm(`Are you sure you want to delete ${runId ? 'this run' : 'this entire project'}?`)) return;

    setLoading(true);
    try {
      const url = runId 
        ? `${API_BASE}/projects/delete?project_name=${projectName}&run_id=${runId}`
        : `${API_BASE}/projects/delete?project_name=${projectName}`;
      
      const response = await fetch(url, { method: 'DELETE' });
      const data = await response.json();
      
      setSuccess(data.deleted || 'Deleted successfully');
      fetchProjects();
    } catch (err) {
      setError('Failed to delete');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">SwiftPredict</h1>
              <p className="text-gray-600 mt-1">Your compass from data to discovery.</p>
            </div>
            <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
              <button
                onClick={() => setActiveTab('view')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'view'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                View Data
              </button>
              <button
                onClick={() => setActiveTab('log')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'log'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Log Data
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error/Success Messages */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
            {success}
          </div>
        )}

        {loading && (
          <div className="fixed inset-0 bg-black bg-opacity-25 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-lg shadow-xl">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading...</p>
            </div>
          </div>
        )}

        {/* View Data Tab */}
        {activeTab === 'view' && (
          <div className="space-y-8">
            {/* Projects Overview */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Projects Overview</h2>
                <button
                  onClick={fetchProjects}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Refresh
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* ML Projects */}
                <div>
                  <h3 className="text-lg font-medium text-gray-800 mb-4">Machine Learning Projects</h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    {projects.ml.length > 0 ? (
                      <div className="space-y-2">
                        {projects.ml.map((project, idx) => (
                          <div key={idx} className="bg-white p-3 rounded border flex justify-between items-center">
                            <div>
                              <p className="font-medium">{project.project_name}</p>
                              <p className="text-sm text-gray-600">Run: {project.run_id}</p>
                              <p className="text-sm text-gray-600">Model: {project.model_name}</p>
                            </div>
                            <div className="flex space-x-2">
                              <button
                                onClick={() => fetchRunDetails(project.project_name, project.run_id)}
                                className="px-3 py-1 bg-blue-100 text-blue-700 rounded text-sm hover:bg-blue-200"
                              >
                                View Details
                              </button>
                              <button
                                onClick={() => handleDeleteProject(project.project_name, project.run_id)}
                                className="px-3 py-1 bg-red-100 text-red-700 rounded text-sm hover:bg-red-200"
                              >
                                Delete
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-center py-4">No ML projects found</p>
                    )}
                  </div>
                </div>

                {/* DL Projects */}
                <div>
                  <h3 className="text-lg font-medium text-gray-800 mb-4">Deep Learning Projects</h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    {projects.dl.length > 0 ? (
                      <div className="space-y-2">
                        {projects.dl.map((project, idx) => (
                          <div key={idx} className="bg-white p-3 rounded border flex justify-between items-center">
                            <div>
                              <p className="font-medium">{project.project_name}</p>
                              <p className="text-sm text-gray-600">Run: {project.run_id}</p>
                              <p className="text-sm text-gray-600">Model: {project.model_name}</p>
                            </div>
                            <div className="flex space-x-2">
                              <button
                                onClick={() => fetchRunDetails(project.project_name, project.run_id)}
                                className="px-3 py-1 bg-blue-100 text-blue-700 rounded text-sm hover:bg-blue-200"
                              >
                                View Details
                              </button>
                              <button
                                onClick={() => fetchAvailableMetrics(project.project_name)}
                                className="px-3 py-1 bg-green-100 text-green-700 rounded text-sm hover:bg-green-200"
                              >
                                View Metrics
                              </button>
                              <button
                                onClick={() => handleDeleteProject(project.project_name, project.run_id)}
                                className="px-3 py-1 bg-red-100 text-red-700 rounded text-sm hover:bg-red-200"
                              >
                                Delete
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-center py-4">No DL projects found</p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Filter by Status */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Filter Projects by Status</h3>
              <div className="flex space-x-4 mb-4">
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select Status</option>
                  <option value="completed">Completed</option>
                  <option value="running">Running</option>
                  <option value="failed">Failed</option>
                  <option value="pending">Pending</option>
                </select>
                <button
                  onClick={() => fetchProjectsByStatus(statusFilter)}
                  disabled={!statusFilter}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
                >
                  Filter
                </button>
              </div>
              {statusProjects.length > 0 && (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Project</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Run ID</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {statusProjects.map((project, idx) => (
                        <tr key={idx}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {project.project_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {project.run_id}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 py-1 text-xs rounded-full ${
                              project.status === 'completed' ? 'bg-green-100 text-green-800' :
                              project.status === 'failed' ? 'bg-red-100 text-red-800' :
                              'bg-yellow-100 text-yellow-800'
                            }`}>
                              {project.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {new Date(project.created_at).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Run Details */}
            {runDetails.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Run Details</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Project</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Run ID</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Model</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {runDetails.map((run, idx) => (
                        <tr key={idx}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {run.project_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {run.run_id}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {run.model_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {new Date(run.created_at).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Available Metrics */}
            {availableMetrics.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Available Metrics</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {availableMetrics.map((metric, idx) => (
                    <div key={idx} className="bg-gray-50 p-4 rounded-lg">
                      <p className="font-medium">Run ID: {metric.run_id}</p>
                      {metric.metrics && (
                        <p className="text-sm text-gray-600">Metric: {metric.metrics.metric}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Log Data Tab */}
        {activeTab === 'log' && (
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Log Data</h2>
            
            <form onSubmit={handleLogSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Project Name *
                  </label>
                  <input
                    type="text"
                    value={logForm.projectName}
                    onChange={(e) => setLogForm({...logForm, projectName: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Run ID *
                  </label>
                  <input
                    type="text"
                    value={logForm.runId}
                    onChange={(e) => setLogForm({...logForm, runId: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Action Type *
                  </label>
                  <select
                    value={logForm.action}
                    onChange={(e) => setLogForm({...logForm, action: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="log_param">Log Parameter</option>
                    <option value="add_tags">Add Tags</option>
                    <option value="update_status">Update Status</option>
                    <option value="add_notes">Add Notes</option>
                  </select>
                </div>
              </div>

              {/* Conditional Fields Based on Action */}
              {logForm.action === 'log_param' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Parameter Key *
                    </label>
                    <input
                      type="text"
                      value={logForm.key}
                      onChange={(e) => setLogForm({...logForm, key: e.target.value})}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Parameter Value *
                    </label>
                    <input
                      type="text"
                      value={logForm.value}
                      onChange={(e) => setLogForm({...logForm, value: e.target.value})}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      required
                    />
                  </div>
                </div>
              )}

              {logForm.action === 'add_tags' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tags (comma-separated) *
                  </label>
                  <input
                    type="text"
                    value={logForm.tags}
                    onChange={(e) => setLogForm({...logForm, tags: e.target.value})}
                    placeholder="tag1, tag2, tag3"
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
              )}

              {logForm.action === 'update_status' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Status *
                  </label>
                  <select
                    value={logForm.status}
                    onChange={(e) => setLogForm({...logForm, status: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  >
                    <option value="">Select Status</option>
                    <option value="completed">Completed</option>
                    <option value="running">Running</option>
                    <option value="failed">Failed</option>
                    <option value="pending">Pending</option>
                  </select>
                </div>
              )}

              {logForm.action === 'add_notes' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Notes *
                  </label>
                  <textarea
                    value={logForm.notes}
                    onChange={(e) => setLogForm({...logForm, notes: e.target.value})}
                    rows={4}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
              )}

              <div className="flex justify-end space-x-4">
                <button
                  type="button"
                  onClick={() => setLogForm({
                    projectName: '',
                    runId: '',
                    action: 'log_param',
                    key: '',
                    value: '',
                    tags: '',
                    status: '',
                    notes: '',
                    metric: ''
                  })}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
                >
                  Clear
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
                >
                  {loading ? 'Submitting...' : 'Submit'}
                </button>
              </div>
            </form>
          </div>
        )}
      </main>
    </div>
  );
}