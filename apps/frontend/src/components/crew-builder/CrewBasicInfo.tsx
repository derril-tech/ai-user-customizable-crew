'use client';

import { TextInput, Textarea, Select, NumberInput, Switch, Group, Text } from '@mantine/core';
import { CrewData } from '@/hooks/useCrewBuilder';

interface CrewBasicInfoProps {
    data: CrewData;
    onChange: (updates: Partial<CrewData>) => void;
}

export function CrewBasicInfo({ data, onChange }: CrewBasicInfoProps) {
    return (
        <div className="space-y-6">
            <div>
                <Text size="lg" fw={600} className="mb-4">Basic Information</Text>

                <div className="space-y-4">
                    <TextInput
                        label="Crew Name"
                        placeholder="Enter crew name"
                        required
                        value={data.name}
                        onChange={(event) => onChange({ name: event.currentTarget.value })}
                    />

                    <Textarea
                        label="Description"
                        placeholder="Describe what this crew does"
                        rows={3}
                        value={data.description}
                        onChange={(event) => onChange({ description: event.currentTarget.value })}
                    />
                </div>
            </div>

            <div>
                <Text size="lg" fw={600} className="mb-4">Execution Settings</Text>

                <div className="space-y-4">
                    <Select
                        label="Execution Mode"
                        description="How agents should execute tasks"
                        data={[
                            { value: 'sequential', label: 'Sequential - One agent at a time' },
                            { value: 'parallel', label: 'Parallel - Multiple agents simultaneously' },
                        ]}
                        value={data.execution_mode}
                        onChange={(value) => onChange({ execution_mode: value as 'sequential' | 'parallel' })}
                    />

                    <NumberInput
                        label="Max Execution Time (seconds)"
                        description="Maximum time allowed for crew execution"
                        min={60}
                        max={7200}
                        value={data.max_execution_time}
                        onChange={(value) => onChange({ max_execution_time: Number(value) })}
                    />
                </div>
            </div>

            <div>
                <Text size="lg" fw={600} className="mb-4">Advanced Options</Text>

                <div className="space-y-3">
                    <Group justify="space-between">
                        <div>
                            <Text size="sm" fw={500}>Verbose Logging</Text>
                            <Text size="xs" c="dimmed">Enable detailed execution logs</Text>
                        </div>
                        <Switch
                            checked={data.verbose}
                            onChange={(event) => onChange({ verbose: event.currentTarget.checked })}
                        />
                    </Group>

                    <Group justify="space-between">
                        <div>
                            <Text size="sm" fw={500}>Memory</Text>
                            <Text size="xs" c="dimmed">Enable agent memory between tasks</Text>
                        </div>
                        <Switch
                            checked={data.memory}
                            onChange={(event) => onChange({ memory: event.currentTarget.checked })}
                        />
                    </Group>

                    <Group justify="space-between">
                        <div>
                            <Text size="sm" fw={500}>Cache</Text>
                            <Text size="xs" c="dimmed">Cache responses to improve performance</Text>
                        </div>
                        <Switch
                            checked={data.cache}
                            onChange={(event) => onChange({ cache: event.currentTarget.checked })}
                        />
                    </Group>
                </div>
            </div>
        </div>
    );
}
