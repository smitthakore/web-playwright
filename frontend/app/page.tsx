'use client';

import { useState } from 'react';
import CodeEditor from '@/app/components/CodeEditor';
import AgentChat from '@/app/components/AgentChat';
import { apiClient, GenerateResponse } from '@/app/lib/api';
import { FileCode, AlertCircle } from 'lucide-react';

export default function Home() {
  const [pageObjectCode, setPageObjectCode] = useState('# Page Object code will appear here...');
  const [testCode, setTestCode] = useState('# Test code will appear here...');
  const [currentFile, setCurrentFile] = useState<'page' | 'test'>('page');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [projectId] = useState('default');

  const handleGenerate = async (prompt: string): Promise<GenerateResponse> => {
    setIsGenerating(true);
    setError(null);

    try {
      const response = await apiClient.generatePOM({
        prompt,
        project_id: projectId,
      });

      if (response.success) {
        setPageObjectCode(response.page_object_code || '# No page object code generated');
        setTestCode(response.test_code || '# No test code generated');
        return response;
      } else {
        throw new Error(response.error || 'Failed to generate code');
      }
    } catch (err: any) {
      const errorMsg = err.message || 'An error occurred';
      setError(errorMsg);
      throw err;
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="h-screen bg-gray-950 text-white flex flex-col">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FileCode className="w-6 h-6 text-blue-500" />
            <div>
              <h1 className="text-xl font-bold">Playwright POM Generator</h1>
              <p className="text-sm text-gray-400">AI-Powered Browser Automation</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-sm text-gray-400">Project: {projectId}</div>
            <div
              className={`w-2 h-2 rounded-full ${isGenerating ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'}`}
              title={isGenerating ? 'Generating...' : 'Ready'}
            />
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-900/20 border-b border-red-900 px-6 py-3 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-red-500" />
          <span className="text-sm text-red-300">{error}</span>
          <button
            onClick={() => setError(null)}
            className="ml-auto text-red-400 hover:text-red-300"
          >
            ✕
          </button>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Agent Chat */}
        <div className="w-2/5 p-4">
          <AgentChat onGenerate={handleGenerate} isGenerating={isGenerating} />
        </div>

        {/* Right: Code Editor */}
        <div className="flex-1 p-4 flex flex-col">
          {/* File Tabs */}
          <div className="flex gap-2 mb-4">
            <button
              onClick={() => setCurrentFile('page')}
              className={`px-4 py-2 rounded-t-lg transition-colors ${
                currentFile === 'page'
                  ? 'bg-gray-800 text-white border-t border-x border-gray-700'
                  : 'bg-gray-900 text-gray-400 hover:text-white'
              }`}
            >
              📄 Page Object
            </button>
            <button
              onClick={() => setCurrentFile('test')}
              className={`px-4 py-2 rounded-t-lg transition-colors ${
                currentFile === 'test'
                  ? 'bg-gray-800 text-white border-t border-x border-gray-700'
                  : 'bg-gray-900 text-gray-400 hover:text-white'
              }`}
            >
              🧪 Test File
            </button>
          </div>

          {/* Editor */}
          <div className="flex-1">
            <CodeEditor
              code={currentFile === 'page' ? pageObjectCode : testCode}
              fileName={currentFile === 'page' ? 'page_object.py' : 'test_page.py'}
              onChange={(value) => {
                if (currentFile === 'page') {
                  setPageObjectCode(value || '');
                } else {
                  setTestCode(value || '');
                }
              }}
              readOnly={false}
            />
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 border-t border-gray-800 px-6 py-2 text-xs text-gray-500">
        <div className="flex items-center justify-between">
          <div>Playwright Agent v1.0 | Powered by LangGraph + Groq</div>
          <div>Backend: http://localhost:8000</div>
        </div>
      </footer>
    </div>
  );
}