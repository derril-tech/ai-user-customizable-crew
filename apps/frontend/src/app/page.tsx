'use client';

import { Container, Title, Text, Button, Grid, Card, Group, Badge } from '@mantine/core';
import { Plus, Users, Zap, Shield } from 'lucide-react';
import Link from 'next/link';

export default function HomePage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
            {/* Header */}
            <header className="bg-white shadow-sm border-b">
                <Container size="xl" className="py-4">
                    <Group justify="space-between">
                        <Title order={2} className="text-primary-600">AI Crew Platform</Title>
                        <Group>
                            <Link href="/crews">
                                <Button variant="outline">My Crews</Button>
                            </Link>
                            <Link href="/marketplace">
                                <Button variant="outline">Marketplace</Button>
                            </Link>
                            <Link href="/crews/new">
                                <Button leftSection={<Plus size={16} />}>Create Crew</Button>
                            </Link>
                        </Group>
                    </Group>
                </Container>
            </header>

            {/* Hero Section */}
            <Container size="xl" className="py-16">
                <div className="text-center mb-16">
                    <Title order={1} size="3rem" className="mb-6 text-gray-900">
                        Build Custom AI Crews
                    </Title>
                    <Text size="xl" className="mb-8 text-gray-600 max-w-2xl mx-auto">
                        Create, customize, and deploy AI agent crews that work together to solve complex tasks.
                        No coding required.
                    </Text>
                    <Group justify="center">
                        <Link href="/crews/new">
                            <Button size="lg" leftSection={<Plus size={20} />}>
                                Create Your First Crew
                            </Button>
                        </Link>
                        <Link href="/marketplace">
                            <Button size="lg" variant="outline">
                                Browse Templates
                            </Button>
                        </Link>
                    </Group>
                </div>

                {/* Features */}
                <Grid>
                    <Grid.Col span={{ base: 12, md: 4 }}>
                        <Card shadow="sm" padding="lg" radius="md" withBorder className="h-full">
                            <div className="text-center">
                                <Users className="mx-auto mb-4 text-primary-500" size={48} />
                                <Title order={3} className="mb-3">Multi-Agent Crews</Title>
                                <Text className="text-gray-600">
                                    Create teams of specialized AI agents that collaborate to complete complex workflows.
                                </Text>
                            </div>
                        </Card>
                    </Grid.Col>

                    <Grid.Col span={{ base: 12, md: 4 }}>
                        <Card shadow="sm" padding="lg" radius="md" withBorder className="h-full">
                            <div className="text-center">
                                <Zap className="mx-auto mb-4 text-primary-500" size={48} />
                                <Title order={3} className="mb-3">Real-time Monitoring</Title>
                                <Text className="text-gray-600">
                                    Watch your crews work in real-time with live progress tracking and detailed logs.
                                </Text>
                            </div>
                        </Card>
                    </Grid.Col>

                    <Grid.Col span={{ base: 12, md: 4 }}>
                        <Card shadow="sm" padding="lg" radius="md" withBorder className="h-full">
                            <div className="text-center">
                                <Shield className="mx-auto mb-4 text-primary-500" size={48} />
                                <Title order={3} className="mb-3">Enterprise Ready</Title>
                                <Text className="text-gray-600">
                                    Built-in compliance, audit trails, and security features for enterprise deployment.
                                </Text>
                            </div>
                        </Card>
                    </Grid.Col>
                </Grid>

                {/* Recent Activity */}
                <div className="mt-16">
                    <Title order={2} className="mb-8">Recent Activity</Title>
                    <Card shadow="sm" padding="lg" radius="md" withBorder>
                        <Text className="text-center text-gray-500 py-8">
                            No recent activity. Create your first crew to get started!
                        </Text>
                    </Card>
                </div>
            </Container>
        </div>
    );
}
