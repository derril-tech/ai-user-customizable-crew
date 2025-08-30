'use client';

import { useState } from 'react';
import { Container, Title, Stepper, Button, Group, Card } from '@mantine/core';
import { ArrowLeft, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { CrewBasicInfo } from '@/components/crew-builder/CrewBasicInfo';
import { AgentBuilder } from '@/components/crew-builder/AgentBuilder';
import { TaskBuilder } from '@/components/crew-builder/TaskBuilder';
import { CrewReview } from '@/components/crew-builder/CrewReview';
import { useCrewBuilder } from '@/hooks/useCrewBuilder';

export default function NewCrewPage() {
    const [active, setActive] = useState(0);
    const { crewData, updateCrewData, createCrew, isCreating } = useCrewBuilder();

    const nextStep = () => setActive((current) => (current < 3 ? current + 1 : current));
    const prevStep = () => setActive((current) => (current > 0 ? current - 1 : current));

    const handleCreateCrew = async () => {
        try {
            await createCrew();
            // Redirect to crews page or show success message
        } catch (error) {
            console.error('Failed to create crew:', error);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm border-b">
                <Container size="xl" className="py-4">
                    <Group>
                        <Link href="/crews" className="text-primary-600 hover:text-primary-700">
                            <Button variant="subtle" leftSection={<ArrowLeft size={16} />}>
                                Back to Crews
                            </Button>
                        </Link>
                        <Title order={2}>Create New Crew</Title>
                    </Group>
                </Container>
            </header>

            <Container size="lg" className="py-8">
                <Card shadow="sm" padding="xl" radius="md" withBorder>
                    <Stepper active={active} onStepClick={setActive} className="mb-8">
                        <Stepper.Step label="Basic Info" description="Crew details">
                            <CrewBasicInfo
                                data={crewData}
                                onChange={updateCrewData}
                            />
                        </Stepper.Step>

                        <Stepper.Step label="Agents" description="Define AI agents">
                            <AgentBuilder
                                agents={crewData.agents}
                                onChange={(agents) => updateCrewData({ agents })}
                            />
                        </Stepper.Step>

                        <Stepper.Step label="Tasks" description="Configure workflows">
                            <TaskBuilder
                                tasks={crewData.tasks}
                                agents={crewData.agents}
                                onChange={(tasks) => updateCrewData({ tasks })}
                            />
                        </Stepper.Step>

                        <Stepper.Step label="Review" description="Review and create">
                            <CrewReview crewData={crewData} />
                        </Stepper.Step>
                    </Stepper>

                    <Group justify="space-between" className="mt-8">
                        <Button
                            variant="outline"
                            onClick={prevStep}
                            disabled={active === 0}
                            leftSection={<ArrowLeft size={16} />}
                        >
                            Previous
                        </Button>

                        {active < 3 ? (
                            <Button
                                onClick={nextStep}
                                rightSection={<ArrowRight size={16} />}
                            >
                                Next
                            </Button>
                        ) : (
                            <Button
                                onClick={handleCreateCrew}
                                loading={isCreating}
                            >
                                Create Crew
                            </Button>
                        )}
                    </Group>
                </Card>
            </Container>
        </div>
    );
}
