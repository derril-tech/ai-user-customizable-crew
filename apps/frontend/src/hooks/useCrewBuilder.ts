import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { crewsApi } from '@/lib/api';
import { notifications } from '@mantine/notifications';

export interface Agent {
    id: string;
    name: string;
    role: string;
    goal: string;
    backstory: string;
    tools: string[];
    llm_config: {
        model: string;
        temperature: number;
        max_tokens: number;
    };
}

export interface Task {
    id: string;
    description: string;
    expected_output: string;
    agent_id: string;
    tools: string[];
    context: string[];
}

export interface CrewData {
    name: string;
    description: string;
    execution_mode: 'sequential' | 'parallel';
    max_execution_time: number;
    verbose: boolean;
    memory: boolean;
    cache: boolean;
    agents: Agent[];
    tasks: Task[];
}

const initialCrewData: CrewData = {
    name: '',
    description: '',
    execution_mode: 'sequential',
    max_execution_time: 3600,
    verbose: true,
    memory: true,
    cache: true,
    agents: [],
    tasks: [],
};

export function useCrewBuilder() {
    const [crewData, setCrewData] = useState<CrewData>(initialCrewData);

    const createCrewMutation = useMutation({
        mutationFn: async () => {
            // Transform crew data to API format
            const crewConfig = {
                name: crewData.name,
                description: crewData.description,
                execution_mode: crewData.execution_mode,
                max_execution_time: crewData.max_execution_time,
                verbose: crewData.verbose,
                memory: crewData.memory,
                cache: crewData.cache,
            };

            const rolesConfig = {
                roles: crewData.agents.reduce((acc, agent) => {
                    acc[agent.id] = {
                        name: agent.name,
                        role: agent.role,
                        goal: agent.goal,
                        backstory: agent.backstory,
                        tools: agent.tools,
                        llm_config: agent.llm_config,
                    };
                    return acc;
                }, {} as any),
            };

            const workflowsConfig = {
                tasks: crewData.tasks.reduce((acc, task) => {
                    acc[task.id] = {
                        description: task.description,
                        expected_output: task.expected_output,
                        agent: task.agent_id,
                        tools: task.tools,
                        context: task.context,
                    };
                    return acc;
                }, {} as any),
            };

            return crewsApi.create({
                name: crewData.name,
                description: crewData.description,
                crew_config: crewConfig,
                roles_config: rolesConfig,
                workflows_config: workflowsConfig,
                is_template: false,
                is_public: false,
            });
        },
        onSuccess: () => {
            notifications.show({
                title: 'Success',
                message: 'Crew created successfully!',
                color: 'green',
            });
            // Reset form
            setCrewData(initialCrewData);
        },
        onError: (error) => {
            notifications.show({
                title: 'Error',
                message: 'Failed to create crew. Please try again.',
                color: 'red',
            });
            console.error('Failed to create crew:', error);
        },
    });

    const updateCrewData = (updates: Partial<CrewData>) => {
        setCrewData((prev) => ({ ...prev, ...updates }));
    };

    const addAgent = () => {
        const newAgent: Agent = {
            id: `agent_${Date.now()}`,
            name: '',
            role: '',
            goal: '',
            backstory: '',
            tools: [],
            llm_config: {
                model: 'gpt-4',
                temperature: 0.7,
                max_tokens: 2000,
            },
        };
        setCrewData((prev) => ({
            ...prev,
            agents: [...prev.agents, newAgent],
        }));
    };

    const updateAgent = (id: string, updates: Partial<Agent>) => {
        setCrewData((prev) => ({
            ...prev,
            agents: prev.agents.map((agent) =>
                agent.id === id ? { ...agent, ...updates } : agent
            ),
        }));
    };

    const removeAgent = (id: string) => {
        setCrewData((prev) => ({
            ...prev,
            agents: prev.agents.filter((agent) => agent.id !== id),
            tasks: prev.tasks.filter((task) => task.agent_id !== id),
        }));
    };

    const addTask = () => {
        const newTask: Task = {
            id: `task_${Date.now()}`,
            description: '',
            expected_output: '',
            agent_id: crewData.agents[0]?.id || '',
            tools: [],
            context: [],
        };
        setCrewData((prev) => ({
            ...prev,
            tasks: [...prev.tasks, newTask],
        }));
    };

    const updateTask = (id: string, updates: Partial<Task>) => {
        setCrewData((prev) => ({
            ...prev,
            tasks: prev.tasks.map((task) =>
                task.id === id ? { ...task, ...updates } : task
            ),
        }));
    };

    const removeTask = (id: string) => {
        setCrewData((prev) => ({
            ...prev,
            tasks: prev.tasks.filter((task) => task.id !== id),
        }));
    };

    return {
        crewData,
        updateCrewData,
        addAgent,
        updateAgent,
        removeAgent,
        addTask,
        updateTask,
        removeTask,
        createCrew: createCrewMutation.mutate,
        isCreating: createCrewMutation.isPending,
    };
}
