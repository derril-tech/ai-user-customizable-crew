'use client';

import { useState } from 'react';
import { Container, Title, Button, Grid, Card, Text, Group, Badge, ActionIcon, Menu } from '@mantine/core';
import { Plus, MoreVertical, Play, Edit, Trash2 } from 'lucide-react';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { crewsApi } from '@/lib/api';

export default function CrewsPage() {
    const { data: crews, isLoading } = useQuery({
        queryKey: ['crews'],
        queryFn: crewsApi.list,
    });

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm border-b">
                <Container size="xl" className="py-4">
                    <Group justify="space-between">
                        <div>
                            <Link href="/" className="text-primary-600 hover:text-primary-700">
                                <Title order={2}>AI Crew Platform</Title>
                            </Link>
                        </div>
                        <Group>
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

            <Container size="xl" className="py-8">
                <div className="mb-8">
                    <Title order={1} className="mb-2">My Crews</Title>
                    <Text className="text-gray-600">
                        Manage and monitor your AI agent crews
                    </Text>
                </div>

                {isLoading ? (
                    <div className="text-center py-8">
                        <Text>Loading crews...</Text>
                    </div>
                ) : crews && crews.length > 0 ? (
                    <Grid>
                        {crews.map((crew) => (
                            <Grid.Col key={crew.id} span={{ base: 12, md: 6, lg: 4 }}>
                                <Card shadow="sm" padding="lg" radius="md" withBorder className="h-full">
                                    <Group justify="space-between" className="mb-3">
                                        <Badge color={crew.is_template ? 'blue' : 'green'} variant="light">
                                            {crew.is_template ? 'Template' : 'Custom'}
                                        </Badge>
                                        <Menu shadow="md" width={200}>
                                            <Menu.Target>
                                                <ActionIcon variant="subtle" color="gray">
                                                    <MoreVertical size={16} />
                                                </ActionIcon>
                                            </Menu.Target>
                                            <Menu.Dropdown>
                                                <Menu.Item leftSection={<Play size={14} />}>
                                                    Run Crew
                                                </Menu.Item>
                                                <Menu.Item leftSection={<Edit size={14} />}>
                                                    Edit
                                                </Menu.Item>
                                                <Menu.Divider />
                                                <Menu.Item leftSection={<Trash2 size={14} />} color="red">
                                                    Delete
                                                </Menu.Item>
                                            </Menu.Dropdown>
                                        </Menu>
                                    </Group>

                                    <Title order={4} className="mb-2">{crew.name}</Title>
                                    <Text size="sm" className="text-gray-600 mb-4 line-clamp-3">
                                        {crew.description || 'No description provided'}
                                    </Text>

                                    <div className="mt-auto">
                                        <Group justify="space-between">
                                            <Text size="xs" className="text-gray-500">
                                                Created {new Date(crew.created_at).toLocaleDateString()}
                                            </Text>
                                            <Link href={`/crews/${crew.id}`}>
                                                <Button size="xs" variant="light">
                                                    View Details
                                                </Button>
                                            </Link>
                                        </Group>
                                    </div>
                                </Card>
                            </Grid.Col>
                        ))}
                    </Grid>
                ) : (
                    <Card shadow="sm" padding="xl" radius="md" withBorder className="text-center">
                        <Title order={3} className="mb-4 text-gray-600">No crews yet</Title>
                        <Text className="mb-6 text-gray-500">
                            Create your first AI crew to get started with automated workflows
                        </Text>
                        <Link href="/crews/new">
                            <Button leftSection={<Plus size={16} />}>
                                Create Your First Crew
                            </Button>
                        </Link>
                    </Card>
                )}
            </Container>
        </div>
    );
}
