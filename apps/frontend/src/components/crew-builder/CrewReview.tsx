'use client';

import { Card, Text, Badge, Group, Divider, List } from '@mantine/core';
import { Users, Zap, Settings, CheckCircle } from 'lucide-react';
import { CrewData } from '@/hooks/useCrewBuilder';

interface CrewReviewProps {
    crewData: CrewData;
}

export function CrewReview({ crewData }: CrewReviewProps) {
    return (
        <div className="space-y-6">
            <Text size="lg" fw={600}>Review Your Crew</Text>

            {/* Basic Info */}
            <Card shadow="sm" padding="lg" radius="md" withBorder>
                <Group className="mb-3">
                    <Settings size={20} className="text-blue-500" />
                    <Text fw={600}>Basic Information</Text>
                </Group>

                <div className="space-y-2">
                    <Group>
                        <Text size="sm" fw={500}>Name:</Text>
                        <Text size="sm">{crewData.name || 'Unnamed Crew'}</Text>
                    </Group>

                    <Group>
                        <Text size="sm" fw={500}>Description:</Text>
                        <Text size="sm" c="dimmed">
                            {crewData.description || 'No description provided'}
                        </Text>
                    </Group>

                    <Group>
                        <Text size="sm" fw={500}>Execution Mode:</Text>
                        <Badge variant="light" color={crewData.execution_mode === 'sequential' ? 'blue' : 'green'}>
                            {crewData.execution_mode}
                        </Badge>
                    </Group>

                    <Group>
                        <Text size="sm" fw={500}>Max Execution Time:</Text>
                        <Text size="sm">{crewData.max_execution_time} seconds</Text>
                    </Group>
                </div>
            </Card>

            {/* Agents */}
            <Card shadow="sm" padding="lg" radius="md" withBorder>
                <Group className="mb-3">
                    <Users size={20} className="text-green-500" />
                    <Text fw={600}>Agents ({crewData.agents.length})</Text>
                </Group>

                {crewData.agents.length === 0 ? (
                    <Text size="sm" c="dimmed">No agents configured</Text>
                ) : (
                    <div className="space-y-3">
                        {crewData.agents.map((agent, index) => (
                            <Card key={agent.id} padding="sm" radius="sm" withBorder className="bg-gray-50">
                                <Group justify="space-between" className="mb-2">
                                    <Group>
                                        <Badge size="sm" variant="outline">Agent {index + 1}</Badge>
                                        <Text size="sm" fw={500}>{agent.name}</Text>
                                    </Group>
                                    <Badge size="sm" color="blue">{agent.llm_config.model}</Badge>
                                </Group>

                                <Text size="xs" c="dimmed" className="mb-1">
                                    <strong>Role:</strong> {agent.role}
                                </Text>
                                <Text size="xs" c="dimmed">
                                    <strong>Goal:</strong> {agent.goal}
                                </Text>
                            </Card>
                        ))}
                    </div>
                )}
            </Card>

            {/* Tasks */}
            <Card shadow="sm" padding="lg" radius="md" withBorder>
                <Group className="mb-3">
                    <Zap size={20} className="text-orange-500" />
                    <Text fw={600}>Tasks ({crewData.tasks.length})</Text>
                </Group>

                {crewData.tasks.length === 0 ? (
                    <Text size="sm" c="dimmed">No tasks configured</Text>
                ) : (
                    <div className="space-y-3">
                        {crewData.tasks.map((task, index) => {
                            const assignedAgent = crewData.agents.find(agent => agent.id === task.agent_id);

                            return (
                                <Card key={task.id} padding="sm" radius="sm" withBorder className="bg-gray-50">
                                    <Group justify="space-between" className="mb-2">
                                        <Group>
                                            <Badge size="sm" variant="outline">Task {index + 1}</Badge>
                                            <Text size="sm" fw={500}>{task.description}</Text>
                                        </Group>
                                        <Badge size="sm" color="green">
                                            {assignedAgent?.name || 'Unassigned'}
                                        </Badge>
                                    </Group>

                                    <Text size="xs" c="dimmed">
                                        <strong>Expected Output:</strong> {task.expected_output}
                                    </Text>

                                    {index > 0 && (
                                        <Text size="xs" c="blue" className="mt-1">
                                            ↳ Depends on Task {index}
                                        </Text>
                                    )}
                                </Card>
                            );
                        })}
                    </div>
                )}
            </Card>

            {/* Validation */}
            <Card shadow="sm" padding="lg" radius="md" withBorder>
                <Group className="mb-3">
                    <CheckCircle size={20} className="text-green-500" />
                    <Text fw={600}>Validation</Text>
                </Group>

                <List spacing="xs" size="sm">
                    <List.Item
                        icon={
                            crewData.name ?
                                <CheckCircle size={16} className="text-green-500" /> :
                                <div className="w-4 h-4 rounded-full border-2 border-gray-300" />
                        }
                    >
                        Crew name provided
                    </List.Item>

                    <List.Item
                        icon={
                            crewData.agents.length > 0 ?
                                <CheckCircle size={16} className="text-green-500" /> :
                                <div className="w-4 h-4 rounded-full border-2 border-gray-300" />
                        }
                    >
                        At least one agent configured
                    </List.Item>

                    <List.Item
                        icon={
                            crewData.tasks.length > 0 ?
                                <CheckCircle size={16} className="text-green-500" /> :
                                <div className="w-4 h-4 rounded-full border-2 border-gray-300" />
                        }
                    >
                        At least one task configured
                    </List.Item>

                    <List.Item
                        icon={
                            crewData.agents.every(agent => agent.name && agent.role && agent.goal) ?
                                <CheckCircle size={16} className="text-green-500" /> :
                                <div className="w-4 h-4 rounded-full border-2 border-gray-300" />
                        }
                    >
                        All agents have required fields
                    </List.Item>

                    <List.Item
                        icon={
                            crewData.tasks.every(task => task.description && task.expected_output && task.agent_id) ?
                                <CheckCircle size={16} className="text-green-500" /> :
                                <div className="w-4 h-4 rounded-full border-2 border-gray-300" />
                        }
                    >
                        All tasks have required fields
                    </List.Item>
                </List>
            </Card>
        </div>
    );
}
