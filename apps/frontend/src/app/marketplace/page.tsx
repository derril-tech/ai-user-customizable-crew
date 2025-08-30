'use client';

import { Container, Title, Text, Grid, Card, Button, Group, Badge } from '@mantine/core';
import { ArrowLeft, Play, Download } from 'lucide-react';
import Link from 'next/link';

const sampleCrews = [
    {
        id: 1,
        name: 'Content Marketing Crew',
        description: 'A team of AI agents that research topics, write blog posts, and create social media content.',
        agents: ['Research Agent', 'Writer Agent', 'Social Media Agent'],
        tasks: ['Topic Research', 'Blog Writing', 'Social Media Posts'],
        category: 'Marketing',
        downloads: 245,
    },
    {
        id: 2,
        name: 'Code Review Crew',
        description: 'Automated code review team that analyzes code quality, security, and performance.',
        agents: ['Security Analyst', 'Performance Reviewer', 'Code Quality Checker'],
        tasks: ['Security Analysis', 'Performance Review', 'Quality Assessment'],
        category: 'Development',
        downloads: 189,
    },
    {
        id: 3,
        name: 'Customer Support Crew',
        description: 'AI-powered customer support team that handles inquiries, escalations, and follow-ups.',
        agents: ['Support Agent', 'Escalation Handler', 'Follow-up Agent'],
        tasks: ['Initial Response', 'Issue Resolution', 'Customer Follow-up'],
        category: 'Support',
        downloads: 156,
    },
    {
        id: 4,
        name: 'Data Analysis Crew',
        description: 'Comprehensive data analysis team that processes, analyzes, and reports on datasets.',
        agents: ['Data Processor', 'Statistical Analyst', 'Report Generator'],
        tasks: ['Data Processing', 'Statistical Analysis', 'Report Generation'],
        category: 'Analytics',
        downloads: 203,
    },
];

const categories = ['All', 'Marketing', 'Development', 'Support', 'Analytics'];

export default function MarketplacePage() {
    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm border-b">
                <Container size="xl" className="py-4">
                    <Group>
                        <Link href="/" className="text-primary-600 hover:text-primary-700">
                            <Button variant="subtle" leftSection={<ArrowLeft size={16} />}>
                                Back to Home
                            </Button>
                        </Link>
                        <Title order={2}>Crew Marketplace</Title>
                    </Group>
                </Container>
            </header>

            <Container size="xl" className="py-8">
                <div className="mb-8">
                    <Title order={1} className="mb-2">Crew Templates</Title>
                    <Text className="text-gray-600">
                        Discover and use pre-built AI crew templates to get started quickly
                    </Text>
                </div>

                {/* Category Filter */}
                <div className="mb-8">
                    <Group>
                        {categories.map((category) => (
                            <Button
                                key={category}
                                variant={category === 'All' ? 'filled' : 'outline'}
                                size="sm"
                            >
                                {category}
                            </Button>
                        ))}
                    </Group>
                </div>

                {/* Crew Templates Grid */}
                <Grid>
                    {sampleCrews.map((crew) => (
                        <Grid.Col key={crew.id} span={{ base: 12, md: 6, lg: 4 }}>
                            <Card shadow="sm" padding="lg" radius="md" withBorder className="h-full">
                                <Group justify="space-between" className="mb-3">
                                    <Badge color="blue" variant="light">
                                        {crew.category}
                                    </Badge>
                                    <Text size="xs" c="dimmed">
                                        {crew.downloads} downloads
                                    </Text>
                                </Group>

                                <Title order={4} className="mb-2">{crew.name}</Title>
                                <Text size="sm" className="text-gray-600 mb-4 line-clamp-3">
                                    {crew.description}
                                </Text>

                                <div className="mb-4">
                                    <Text size="sm" fw={500} className="mb-2">Agents:</Text>
                                    <div className="flex flex-wrap gap-1">
                                        {crew.agents.map((agent, index) => (
                                            <Badge key={index} size="xs" variant="outline">
                                                {agent}
                                            </Badge>
                                        ))}
                                    </div>
                                </div>

                                <div className="mb-6">
                                    <Text size="sm" fw={500} className="mb-2">Tasks:</Text>
                                    <div className="flex flex-wrap gap-1">
                                        {crew.tasks.map((task, index) => (
                                            <Badge key={index} size="xs" variant="dot">
                                                {task}
                                            </Badge>
                                        ))}
                                    </div>
                                </div>

                                <div className="mt-auto">
                                    <Group>
                                        <Button
                                            size="sm"
                                            leftSection={<Download size={14} />}
                                            variant="outline"
                                            className="flex-1"
                                        >
                                            Use Template
                                        </Button>
                                        <Button
                                            size="sm"
                                            leftSection={<Play size={14} />}
                                            className="flex-1"
                                        >
                                            Preview
                                        </Button>
                                    </Group>
                                </div>
                            </Card>
                        </Grid.Col>
                    ))}
                </Grid>

                {/* Call to Action */}
                <Card shadow="sm" padding="xl" radius="md" withBorder className="mt-12 text-center bg-gradient-to-r from-blue-50 to-indigo-50">
                    <Title order={3} className="mb-4">Can't find what you're looking for?</Title>
                    <Text className="mb-6 text-gray-600">
                        Create your own custom AI crew from scratch with our intuitive builder
                    </Text>
                    <Link href="/crews/new">
                        <Button size="lg" leftSection={<Play size={20} />}>
                            Create Custom Crew
                        </Button>
                    </Link>
                </Card>
            </Container>
        </div>
    );
}
