import axios from 'axios';

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Types
export interface Crew {
    id: number;
    name: string;
    description?: string;
    crew_config?: any;
    roles_config?: any;
    workflows_config?: any;
    is_template: boolean;
    is_public: boolean;
    organization_id: number;
    created_by_id: number;
    created_at: string;
    updated_at: string;
}

export interface CrewCreate {
    name: string;
    description?: string;
    crew_config?: any;
    roles_config?: any;
    workflows_config?: any;
    is_template?: boolean;
    is_public?: boolean;
}

export interface Job {
    id: number;
    status: string;
    input_data: any;
    output_data?: any;
    error_message?: string;
    cost_usd?: number;
    tokens_used?: number;
    execution_time_seconds?: number;
    crew_id: number;
    created_by_id: number;
    started_at?: string;
    completed_at?: string;
    created_at: string;
    updated_at: string;
}

export interface JobCreate {
    input_data: any;
}

// API functions
export const crewsApi = {
    list: async (): Promise<Crew[]> => {
        const response = await api.get('/v1/crews');
        return response.data;
    },

    get: async (id: number): Promise<Crew> => {
        const response = await api.get(`/v1/crews/${id}`);
        return response.data;
    },

    create: async (data: CrewCreate): Promise<Crew> => {
        const response = await api.post('/v1/crews', data);
        return response.data;
    },

    update: async (id: number, data: Partial<CrewCreate>): Promise<Crew> => {
        const response = await api.put(`/v1/crews/${id}`, data);
        return response.data;
    },

    delete: async (id: number): Promise<void> => {
        await api.delete(`/v1/crews/${id}`);
    },

    run: async (id: number, data: JobCreate): Promise<Job> => {
        const response = await api.post(`/v1/crews/${id}/run`, data);
        return response.data;
    },
};

export const jobsApi = {
    list: async (): Promise<Job[]> => {
        const response = await api.get('/v1/jobs');
        return response.data;
    },

    get: async (id: number): Promise<Job> => {
        const response = await api.get(`/v1/jobs/${id}`);
        return response.data;
    },

    stream: (id: number): EventSource => {
        return new EventSource(`${api.defaults.baseURL}/v1/jobs/${id}/stream`);
    },
};

export default api;
