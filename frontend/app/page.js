'use client';
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import {
  Clock, Activity, Target, Database, TrendingUp, Award,
  Home, FileText, Settings, Play, BarChart3, Upload,
  Compass, Search, Filter, RefreshCw
} from 'lucide-react';

const SwiftPredictDashboard = () => {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [projects, setProjects] = useState([]);
  const [runs, setRuns] = useState([]);
  const [selectedProject, setSelectedProject] = useState('');
  const [selectedRunId, setSelectedRunId] = useState('');
  const [metricsData, setMetricsData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // API Base URL - adjust this to match your FastAPI server
  const API_BASE = 'http://localhost:9000';

  // Fetch all projects
  const fetchProjects = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/projects`);
      if (response.ok) {
        const data = await response.json();
        setProjects(Array.isArray(data) ? data : []);
      } else {
        setError('Failed to fetch projects');
      }
    } catch (err) {
      setError(`Error fetching projects: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Fetch run data for a specific project and run ID
  const fetchRunData = async (projectName, runId) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/${projectName}/runs/${runId}`);
      if (response.ok) {
        const data = await response.json();
        return data;
      } else {
        setError(`Failed to fetch run data for ${runId}`);
        return null;
      }
    } catch (err) {
      setError(`Error fetching run data: ${err.message}`);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Fetch metrics plot data
  const fetchMetricsPlot = async (projectName, runId, metric) => {
    try {
      const response = await fetch(`${API_BASE}/${projectName}/plots?metric=${metric}&run_id=${runId}&project_name=${projectName}`);
      if (response.ok) {
        // Note: Your API returns a streaming image, but for chart data we'd need a JSON endpoint
        // This is a placeholder - you might want to add a separate endpoint that returns chart data as JSON
        return null;
      }
    } catch (err) {
      console.error(`Error fetching metrics: ${err.message}`);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed': return 'bg-green-100 text-green-800 border-green-200';
      case 'running': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'failed': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  // Navigation component
  const Navigation = () => (
    <nav className="bg-white border-b border-sandstone shadow-sm">
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <Button
              variant={currentPage === 'dashboard' ? 'default' : 'ghost'}
              onClick={() => setCurrentPage('dashboard')}
              className="flex items-center space-x-2"
            >
              <Home className="w-4 h-4" />
              <span>Dashboard</span>
            </Button>
            <Button
              variant={currentPage === 'logger-get' ? 'default' : 'ghost'}
              onClick={() => setCurrentPage('logger-get')}
              className="flex items-center space-x-2"
            >
              <Search className="w-4 h-4" />
              <span>Logger (GET)</span>
            </Button>
            <Button
              variant={currentPage === 'logger-post' ? 'default' : 'ghost'}
              onClick={() => setCurrentPage('logger-post')}
              className="flex items-center space-x-2"
            >
              <FileText className="w-4 h-4" />
              <span>Logger (POST)</span>
            </Button>
            <Button
              variant={currentPage === 'automl' ? 'default' : 'ghost'}
              onClick={() => setCurrentPage('automl')}
              className="flex items-center space-x-2"
            >
              <BarChart3 className="w-4 h-4" />
              <span>AutoML</span>
            </Button>
          </div>
          <Button onClick={fetchProjects} variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>
    </nav>
  );

  // Dashboard Overview Page
  const DashboardPage = () => (
    <div className="space-y-6">
      <div className="grid md:grid-cols-4 gap-4">
        <Card className="bg-white border-sandstone shadow">
          <CardContent className="p-6 text-center">
            <Database className="w-8 h-8 text-golden mx-auto mb-2" />
            <div className="text-2xl font-bold text-golden">{projects.length}</div>
            <div className="text-sm text-cocoa">Total Projects</div>
          </CardContent>
        </Card>
        <Card className="bg-white border-sandstone shadow">
          <CardContent className="p-6 text-center">
            <Activity className="w-8 h-8 text-ochre mx-auto mb-2" />
            <div className="text-2xl font-bold text-ochre">{runs.length}</div>
            <div className="text-sm text-cocoa">Total Runs</div>
          </CardContent>
        </Card>
        <Card className="bg-white border-sandstone shadow">
          <CardContent className="p-6 text-center">
            <TrendingUp className="w-8 h-8 text-sienna mx-auto mb-2" />
            <div className="text-2xl font-bold text-sienna">Live</div>
            <div className="text-sm text-cocoa">API Status</div>
          </CardContent>
        </Card>
        <Card className="bg-white border-sandstone shadow">
          <CardContent className="p-6 text-center">
            <Award className="w-8 h-8 text-golden mx-auto mb-2" />
            <div className="text-2xl font-bold text-golden">Ready</div>
            <div className="text-sm text-cocoa">System Status</div>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-white border-sandstone shadow-lg">
        <CardHeader>
          <CardTitle className="text-umber">Available Projects</CardTitle>
          <CardDescription className="text-cocoa">Click on a project to explore its runs</CardDescription>
        </CardHeader>
        <CardContent>
          {projects.length > 0 ? (
            <div className="grid md:grid-cols-3 gap-4">
              {projects.map((project, index) => (
                <Card key={index} className="border border-sandstone hover:shadow-lg transition-shadow cursor-pointer"
                      onClick={() => setSelectedProject(project)}>
                  <CardContent className="p-4 text-center">
                    <Target className="w-8 h-8 text-golden mx-auto mb-2" />
                    <div className="font-semibold text-umber">{project}</div>
                    <div className="text-sm text-cocoa mt-1">Click to explore</div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-cocoa">
              {loading ? 'Loading projects...' : 'No projects found. Start by creating your first experiment!'}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );

  // Logger GET APIs Page
  const LoggerGetPage = () => (
    <div className="space-y-6">
      <Card className="bg-white border-sandstone shadow-lg">
        <CardHeader>
          <CardTitle className="text-umber flex items-center">
            <Search className="w-5 h-5 mr-2" />
            Logger GET APIs
          </CardTitle>
          <CardDescription className="text-cocoa">Fetch and view your experiment data</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-umber mb-2">Select Project</label>
              <select
                className="w-full p-2 border border-sandstone rounded-md bg-white text-umber"
                value={selectedProject}
                onChange={(e) => setSelectedProject(e.target.value)}
              >
                <option value="">Choose a project...</option>
                {projects.map((project, index) => (
                  <option key={index} value={project}>{project}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-umber mb-2">Run ID</label>
              <Input
                placeholder="Enter run ID..."
                value={selectedRunId}
                onChange={(e) => setSelectedRunId(e.target.value)}
                className="border-sandstone"
              />
            </div>
          </div>
          <Button
            onClick={() => selectedProject && selectedRunId && fetchRunData(selectedProject, selectedRunId)}
            className="bg-golden hover:bg-ochre text-white"
            disabled={!selectedProject || !selectedRunId || loading}
          >
            {loading ? 'Fetching...' : 'Fetch Run Data'}
          </Button>
        </CardContent>
      </Card>

      <Card className="bg-white border-sandstone shadow-lg">
        <CardHeader>
          <CardTitle className="text-umber">Available GET Endpoints</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm">
            <div className="p-3 bg-tan rounded border border-sandstone">
              <code className="text-umber font-mono">GET /projects</code>
              <p className="text-cocoa mt-1">Get all distinct projects</p>
            </div>
            <div className="p-3 bg-tan rounded border border-sandstone">
              <code className="text-umber font-mono">GET /{'{project_name}'}/runs/{'{run_id}'}</code>
              <p className="text-cocoa mt-1">Fetch all data for a specific run</p>
            </div>
            <div className="p-3 bg-tan rounded border border-sandstone">
              <code className="text-umber font-mono">GET /{'{project_name}'}/plots</code>
              <p className="text-cocoa mt-1">Generate metric visualization plots</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  // Logger POST APIs Page
  const LoggerPostPage = () => (
    <div className="space-y-6">
      <Card className="bg-white border-sandstone shadow-lg">
        <CardHeader>
          <CardTitle className="text-umber flex items-center">
            <FileText className="w-5 h-5 mr-2" />
            Logger POST APIs
          </CardTitle>
          <CardDescription className="text-cocoa">Log parameters, metrics, and experiment metadata</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            {/* Log Parameters */}
            <Card className="border border-sandstone">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm text-umber">Log Parameters</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Input placeholder="Parameter key" className="border-sandstone" />
                <Input placeholder="Parameter value" className="border-sandstone" />
                <Input placeholder="Run ID" className="border-sandstone" />
                <Input placeholder="Project name" className="border-sandstone" />
                <Button className="w-full bg-golden hover:bg-ochre text-white">
                  Log Parameter
                </Button>
              </CardContent>
            </Card>

            {/* Log Metrics */}
            <Card className="border border-sandstone">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm text-umber">Log Metrics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Input placeholder="Metric name" className="border-sandstone" />
                <Input placeholder="Metric value" className="border-sandstone" />
                <Input placeholder="Step/Iteration" className="border-sandstone" />
                <Input placeholder="Run ID" className="border-sandstone" />
                <Button className="w-full bg-golden hover:bg-ochre text-white">
                  Log Metric
                </Button>
              </CardContent>
            </Card>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-white border-sandstone shadow-lg">
        <CardHeader>
          <CardTitle className="text-umber">Available POST Endpoints</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm">
            <div className="p-3 bg-tan rounded border border-sandstone">
              <code className="text-umber font-mono">POST /{'{project_name}'}/runs/{'{run_id}'}/log_param</code>
              <p className="text-cocoa mt-1">Log training parameters</p>
            </div>
            <div className="p-3 bg-tan rounded border border-sandstone">
              <code className="text-umber font-mono">POST /{'{project_name}'}/runs/{'{run_id}'}/log_metric</code>
              <p className="text-cocoa mt-1">Log evaluation metrics</p>
            </div>
            <div className="p-3 bg-tan rounded border border-sandstone">
              <code className="text-umber font-mono">POST /{'{project_name}'}/runs/{'{run_id}'}/add_tags</code>
              <p className="text-cocoa mt-1">Add tags to runs</p>
            </div>
            <div className="p-3 bg-tan rounded border border-sandstone">
              <code className="text-umber font-mono">POST /{'{project_name}'}/runs/{'{run_id}'}/update_status</code>
              <p className="text-cocoa mt-1">Update run status</p>
            </div>
            <div className="p-3 bg-tan rounded border border-sandstone">
              <code className="text-umber font-mono">POST /{'{project_name}'}/runs/{'{run_id}'}/add_notes</code>
              <p className="text-cocoa mt-1">Add experiment notes</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  // AutoML APIs Page
  const AutoMLPage = () => (
    <div className="space-y-6">
      <Card className="bg-white border-sandstone shadow-lg">
        <CardHeader>
          <CardTitle className="text-umber flex items-center">
            <BarChart3 className="w-5 h-5 mr-2" />
            AutoML APIs
          </CardTitle>
          <CardDescription className="text-cocoa">Train models and make predictions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            {/* Train Model */}
            <Card className="border border-sandstone">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm text-umber flex items-center">
                  <Play className="w-4 h-4 mr-2" />
                  Train Model
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <label className="block text-xs text-cocoa mb-1">Dataset File</label>
                  <div className="flex items-center space-x-2">
                    <Input type="file" accept=".csv" className="border-sandstone" />
                    <Upload className="w-4 h-4 text-golden" />
                  </div>
                </div>
                <Input placeholder="Project name" className="border-sandstone" />
                <Input placeholder="Target column name" className="border-sandstone" />
                <Button className="w-full bg-golden hover:bg-ochre text-white">
                  Start Training
                </Button>
              </CardContent>
            </Card>

            {/* Make Predictions */}
            <Card className="border border-sandstone">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm text-umber flex items-center">
                  <Target className="w-4 h-4 mr-2" />
                  Make Predictions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <label className="block text-xs text-cocoa mb-1">Input Data</label>
                  <textarea
                    placeholder="Enter data for prediction..."
                    className="w-full p-2 border border-sandstone rounded-md bg-white text-umber h-20 resize-none"
                  />
                </div>
                <Button className="w-full bg-golden hover:bg-ochre text-white">
                  Get Predictions
                </Button>
              </CardContent>
            </Card>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-white border-sandstone shadow-lg">
        <CardHeader>
          <CardTitle className="text-umber">Available AutoML Endpoints</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm">
            <div className="p-3 bg-tan rounded border border-sandstone">
              <code className="text-umber font-mono">POST /automl/train</code>
              <p className="text-cocoa mt-1">Train AutoML models on your dataset</p>
              <p className="text-xs text-cocoa mt-1">Parameters: file, project_name, target_column</p>
            </div>
            <div className="p-3 bg-tan rounded border border-sandstone">
              <code className="text-umber font-mono">GET /automl/predict</code>
              <p className="text-cocoa mt-1">Make predictions using trained models</p>
              <p className="text-xs text-cocoa mt-1">Parameters: data</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  if (loading && currentPage === 'dashboard') {
    return (
      <div className="min-h-screen bg-almond flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 text-golden animate-spin mx-auto mb-4" />
          <div className="text-umber text-lg">Loading SwiftPredict Dashboard...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-almond">
      {/* Header */}
      <header className="bg-gradient-to-r from-golden to-ochre text-white shadow-lg">
        <div className="container mx-auto px-6 py-8">
          <div className="flex items-center space-x-4">
            <Compass className="h-12 w-12" />
            <div>
              <h1 className="text-4xl font-bold">SwiftPredict</h1>
              <p className="text-xl opacity-90">Your compass from data to discovery</p>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <Navigation />

      {/* Error Display */}
      {error && (
        <div className="container mx-auto px-6 py-4">
          <div className="bg-red-100 border border-red-200 text-red-800 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {currentPage === 'dashboard' && <DashboardPage />}
        {currentPage === 'logger-get' && <LoggerGetPage />}
        {currentPage === 'logger-post' && <LoggerPostPage />}
        {currentPage === 'automl' && <AutoMLPage />}
      </main>
    </div>
  );
};

export default SwiftPredictDashboard;