'use client';

import { Button, Card, TextInput, Textarea, Select, NumberInput, Group, Text, ActionIcon, Badge } from '@mantine/core';
import { Plus, Trash2 } from 'lucide-react';
import { Agent } from '@/hooks/useCrewBuilder';

interface AgentBuilderProps {
    agents: Agent[];
    onChange: (agents: Agent[]) => void;
}

export function AgentBuilder({ agents, onChange }: AgentBuilderProps) {
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
        onChange([...agents, newAgent]);
    };

    const updateAgent = (id: string, updates: Partial<Agent>) => {
        onChange(
            agents.map((agent) =>
                agent.id === id ? { ...agent, ...updates } : agent
            )
        );
    };

    const removeAgent = (id: string) => {
        onChange(agents.filter((agent) => agent.id !== id));
    };

    return (
        <div className="space-y-6">
            <Group justify="space-between">
                <Text size="lg" fw={600}>AI Agents</Text>
                <Button leftSection={<Plus size={16} />} onClick={addAgent}>
                    Add Agent
                </Button>
            </Group>

            {agents.length === 0 ? (
                <Card shadow="sm" padding="xl" radius="md" withBorder className="text-center">
                    <Text className="mb-4 text-gray-500">No agents added yet</Text>
                    <Button leftSection={<Plus size={16} />} onClick={addAgent}>
                        Add Your First Agent
                    </Button>
                </Card>
            ) : (
                <div className="space-y-4">
                    {agents.map((agent, index) => (
                        <Card key={agent.id} shadow="sm" padding="lg" radius="md" withBorder>
                            <Group justify="space-between" className="mb-4">
                                <Group>
                                    <Badge variant="light">Agent {index + 1}</Badge>
                                    <Text fw={500}>{agent.name || 'Unnamed Agent'}</Text>
                                </Group>
                                <ActionIcon
                                    color="red"
                                    variant="subtle"
                                    onClick={() => removeAgent(agent.id)}
                                >
                                    <Trash2 size={16} />
                                </ActionIcon>
                            </Group>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <TextInput
                                    label="Agent Name"
                                    placeholder="e.g., Research Assistant"
                                    value={agent.name}
                                    onChange={(event) =>
                                        updateAgent(agent.id, { name: event.currentTarget.value })
                                    }
                                />

                                <TextInput
                                    label="Role"
                                    placeholder="e.g., Senior Researcher"
                                    value={agent.role}
                                    onChange={(event) =>
                                        updateAgent(agent.id, { role: event.currentTarget.value })
                                    }
                                />
                            </div>

                            <div className="mt-4 space-y-4">
                                <Textarea
                                    label="Goal"
                                    placeholder="What should this agent accomplish?"
                                    rows={2}
                                    value={agent.goal}
                                    onChange={(event) =>
                                        updateAgent(agent.id, { goal: event.currentTarget.value })
                                    }
                                />

                                <Textarea
                                    label="Backstory"
                                    placeholder="Agent's background and expertise"
                                    rows={3}
                                    value={agent.backstory}
                                    onChange={(event) =>
                                        updateAgent(agent.id, { backstory: event.currentTarget.value })
                                    }
                                />
                            </div>

                            <div className="mt-4">
                                <Text size="sm" fw={500} className="mb-2">LLM Configuration</Text>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <Select
                                        label="Model"
                                        data={[
                                            { value: 'gpt-4', label: 'GPT-4' },
                                            { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
                                            { value: 'claude-3-sonnet', label: 'Claude 3 Sonnet' },
                                        ]}
                                        value={agent.llm_config.model}
                                        onChange={(value) =>
                                            updateAgent(agent.id, {
                                                llm_config: { ...agent.llm_config, model: value || 'gpt-4' }
                                            })
                                        }
                                    />

                                    <NumberInput
                                        label="Temperature"
                                        min={0}
                                        max={2}
                                        step={0.1}
                                        value={agent.llm_config.temperature}
                                        onChange={(value) =>
                                            updateAgent(agent.id, {
                                                llm_config: { ...agent.llm_config, temperature: Number(value) }
                                            })
                                        }
                                    />

                                    <NumberInput
                                        label="Max Tokens"
                                        min={100}
                                        max={8000}
                                        value={agent.llm_config.max_tokens}
                                        onChange={(value) =>
                                            updateAgent(agent.id, {
                                                llm_config: { ...agent.llm_config, max_tokens: Number(value) }
                                            })
                                        }
                                    />
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}
