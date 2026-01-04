import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface GenerateRequest {
  prompt: string;
  project_id?: string;
}

export interface GenerateResponse {
  success: boolean;
  task_type: string;
  page_object_code: string;
  test_code: string;
  class_name: string;
  saved_files: string[];
  extracted_locators: Record<string, string>;
  response: string;
  duration: number;
  iterations: number;
  error?: string;
}

export interface FileInfo {
  name: string;
  path: string;
  type: 'file' | 'directory';
}

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  /**
   * Generate POM code using the agent
   */
  async generatePOM(request: GenerateRequest): Promise<GenerateResponse> {
    try {
      const response = await axios.post(`${this.baseURL}/api/generate`, {
        prompt: request.prompt,
        project_id: request.project_id || 'default',
      });
      return response.data;
    } catch (error: any) {
      console.error('Generate POM error:', error);
      throw new Error(error.response?.data?.detail || 'Failed to generate POM');
    }
  }

  /**
   * List files in workspace
   */
  async listFiles(path: string = '', projectId: string = 'default'): Promise<FileInfo[]> {
    try {
      const response = await axios.get(`${this.baseURL}/api/files/list`, {
        params: { path, project_id: projectId },
      });
      return response.data.files;
    } catch (error: any) {
      console.error('List files error:', error);
      throw new Error(error.response?.data?.detail || 'Failed to list files');
    }
  }

  /**
   * Read file content
   */
  async readFile(path: string): Promise<string> {
    try {
      const response = await axios.get(`${this.baseURL}/api/files/read`, {
        params: { path },
      });
      return response.data.content;
    } catch (error: any) {
      console.error('Read file error:', error);
      throw new Error(error.response?.data?.detail || 'Failed to read file');
    }
  }

  /**
   * Write file content
   */
  async writeFile(path: string, content: string): Promise<boolean> {
    try {
      const response = await axios.post(`${this.baseURL}/api/files/write`, {
        path,
        content,
      });
      return response.data.success;
    } catch (error: any) {
      console.error('Write file error:', error);
      throw new Error(error.response?.data?.detail || 'Failed to write file');
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await axios.get(`${this.baseURL}/health`);
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }
}

export const apiClient = new ApiClient();
export default apiClient;