'use client';

import { Button, Card, TextInput, Textarea, Select, Group, Text, ActionIcon, Badge } from '@mantine/core';
import { Plus, Trash2 } from 'lucide-react';
import { Task, Agent } from '@/hooks/useCrewBuilder';

interface TaskBuilderProps {
    tasks: Task[];
    agents: Agent[];
    onChange: (tasks: Task[]) => void;
}

export function TaskBuilder({ tasks, agents, onChange }: TaskBuilderProps) {
    const addTask = () => {
        const newTask: Task = {
            id: `task_${Date.now()}`,
            description: '',
            expected_output: '',
            agent_id: agents[0]?.id || '',
            tools: [],
            context: [],
        };
        onChange([...tasks, newTask]);
    };

    const updateTask = (id: string, updates: Partial<Task>) => {
        onChange(
            tasks.map((task) =>
                task.id === id ? { ...task, ...updates } : task
            )
        );
    };

    const removeTask = (id: string) => {
        onChange(tasks.filter((task) => task.id !== id));
    };

    const agentOptions = agents.map((agent) => ({
        value: agent.id,
        label: agent.name || `Agent ${agents.indexOf(agent) + 1}`,
    }));

    return (
        <div className="space-y-6">
            <Group justify="space-between">
                <Text size="lg" fw={600}>Workflow Tasks</Text>
                <Button
                    leftSection={<Plus size={16} />}
                    onClick={addTask}
                    disabled={agents.length === 0}
                >
                    Add Task
                </Button>
            </Group>

            {agents.length === 0 ? (
                <Card shadow="sm" padding="xl" radius="md" withBorder className="text-center">
                    <Text className="mb-4 text-gray-500">
                        You need to add agents before creating tasks
                    </Text>
                    <Text size="sm" c="dimmed">
                        Go back to the previous step to add your first agent
                    </Text>
                </Card>
            ) : tasks.length === 0 ? (
                <Card shadow="sm" padding="xl" radius="md" withBorder className="text-center">
                    <Text className="mb-4 text-gray-500">No tasks added yet</Text>
                    <Button leftSection={<Plus size={16} />} onClick={addTask}>
                        Add Your First Task
                    </Button>
                </Card>
            ) : (
                <div className="space-y-4">
                    {tasks.map((task, index) => (
                        <Card key={task.id} shadow="sm" padding="lg" radius="md" withBorder>
                            <Group justify="space-between" className="mb-4">
                                <Group>
                                    <Badge variant="light">Task {index + 1}</Badge>
                                    <Text fw={500}>{task.description || 'Unnamed Task'}</Text>
                                </Group>
                                <ActionIcon
                                    color="red"
                                    variant="subtle"
                                    onClick={() => removeTask(task.id)}
                                >
                                    <Trash2 size={16} />
                                </ActionIcon>
                            </Group>

                            <div className="space-y-4">
                                <Textarea
                                    label="Task Description"
                                    placeholder="Describe what this task should accomplish"
                                    rows={3}
                                    value={task.description}
                                    onChange={(event) =>
                                        updateTask(task.id, { description: event.currentTarget.value })
                                    }
                                />

                                <Textarea
                                    label="Expected Output"
                                    placeholder="Describe the expected result or deliverable"
                                    rows={2}
                                    value={task.expected_output}
                                    onChange={(event) =>
                                        updateTask(task.id, { expected_output: event.currentTarget.value })
                                    }
                                />

                                <Select
                                    label="Assigned Agent"
                                    placeholder="Select an agent to execute this task"
                                    data={agentOptions}
                                    value={task.agent_id}
                                    onChange={(value) =>
                                        updateTask(task.id, { agent_id: value || '' })
                                    }
                                />

                                {index > 0 && (
                                    <div>
                                        <Text size="sm" fw={500} className="mb-2">Task Dependencies</Text>
                                        <Text size="xs" c="dimmed" className="mb-2">
                                            This task will automatically depend on the previous task
                                        </Text>
                                        <Badge variant="outline" size="sm">
                                            Depends on: Task {index}
                                        </Badge>
                                    </div>
                                )}
                            </div>
                        </Card>
                    ))}
                </div>
            )}

            {tasks.length > 0 && (
                <Card shadow="sm" padding="md" radius="md" withBorder className="bg-blue-50">
                    <Text size="sm" fw={500} className="mb-2">Execution Order</Text>
                    <Text size="xs" c="dimmed">
                        Tasks will be executed in the order shown above. Each task will wait for the previous one to complete.
                    </Text>
                </Card>
            )}
        </div>
    );
}
