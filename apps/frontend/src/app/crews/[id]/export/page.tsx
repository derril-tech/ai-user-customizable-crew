'use client';

import { useState } from 'react';
import { Container, Title, Card, Button, Group, Text, Select, Switch, Alert } from '@mantine/core';
import { Download, FileText, Archive, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { crewsApi } from '@/lib/api';

export default function CrewExportPage() {
    const params = useParams();
    const crewId = parseInt(params.id as string);

    const [exportFormat, setExportFormat] = useState('json');
    const [includeMetadata, setIncludeMetadata] = useState(true);
    const [isExporting, setIsExporting] = useState(false);

    const { data: crew, isLoading } = useQuery({
        queryKey: ['crew', crewId],
        queryFn: () => crewsApi.get(crewId),
    });

    const handleExport = async () => {
        setIsExporting(true);

        try {
            const response = await fetch(
                `/api/v1/export/${crewId}/export?format=${exportFormat}&include_metadata=${includeMetadata}`,
                {
                    method: 'GET',
                    headers: {
                        'Accept': exportFormat === 'zip' ? 'application/zip' : 'application/json',
                    },
                }
            );

            if (!response.ok) {
                throw new Error('Export failed');
            }

            // Get filename from response headers
            const contentDisposition = response.headers.get('Content-Disposition');
            const filename = contentDisposition?.match(/filename="(.+)"/)?.[1] ||
                `crew_export_${crewId}.${exportFormat}`;

            // Download file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

        } catch (error) {
            console.error('Export failed:', error);
            // TODO: Show error notification
        } finally {
            setIsExporting(false);
        }
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <Text>Loading crew details...</Text>
            </div>
        );
    }

    if (!crew) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <Text>Crew not found</Text>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm border-b">
                <Container size="xl" className="py-4">
                    <Group>
                        <Link href={`/crews/${crewId}`} className="text-primary-600 hover:text-primary-700">
                            <Button variant="subtle" leftSection={<ArrowLeft size={16} />}>
                                Back to Crew
                            </Button>
                        </Link>
                        <Title order={2}>Export Crew</Title>
                    </Group>
                </Container>
            </header>

            <Container size="md" className="py-8">
                <Card shadow="sm" padding="xl" radius="md" withBorder>
                    <div className="mb-6">
                        <Title order={3} className="mb-2">Export "{crew.name}"</Title>
                        <Text className="text-gray-600">
                            Download your crew configuration for backup, sharing, or deployment to other environments.
                        </Text>
                    </div>

                    <div className="space-y-6">
                        {/* Export Format */}
                        <div>
                            <Text size="sm" fw={500} className="mb-2">Export Format</Text>
                            <Select
                                value={exportFormat}
                                onChange={(value) => setExportFormat(value || 'json')}
                                data={[
                                    {
                                        value: 'json',
                                        label: 'JSON - Single file with all configuration'
                                    },
                                    {
                                        value: 'zip',
                                        label: 'ZIP - Organized files with documentation'
                                    }
                                ]}
                            />
                        </div>

                        {/* Options */}
                        <div>
                            <Text size="sm" fw={500} className="mb-3">Export Options</Text>

                            <Group justify="space-between" className="p-3 bg-gray-50 rounded">
                                <div>
                                    <Text size="sm" fw={500}>Include Metadata</Text>
                                    <Text size="xs" c="dimmed">
                                        Export timestamps, original IDs, and platform version info
                                    </Text>
                                </div>
                                <Switch
                                    checked={includeMetadata}
                                    onChange={(event) => setIncludeMetadata(event.currentTarget.checked)}
                                />
                            </Group>
                        </div>

                        {/* Export Preview */}
                        <Alert color="blue" icon={<FileText size={16} />}>
                            <Text size="sm" fw={500} className="mb-1">Export Contents</Text>
                            <Text size="xs">
                                • Crew configuration and settings<br />
                                • Agent definitions and LLM configs<br />
                                • Task workflows and dependencies<br />
                                {exportFormat === 'zip' && '• README with import instructions<br/>'}
                                {includeMetadata && '• Export metadata and timestamps'}
                            </Text>
                        </Alert>

                        {/* Export Button */}
                        <Group justify="center" className="pt-4">
                            <Button
                                size="lg"
                                leftSection={exportFormat === 'zip' ? <Archive size={20} /> : <Download size={20} />}
                                onClick={handleExport}
                                loading={isExporting}
                            >
                                {isExporting ? 'Exporting...' : `Export as ${exportFormat.toUpperCase()}`}
                            </Button>
                        </Group>

                        {/* Format Details */}
                        <div className="pt-6 border-t">
                            <Text size="sm" fw={500} className="mb-2">Format Details</Text>

                            {exportFormat === 'json' ? (
                                <div className="space-y-2">
                                    <Text size="xs" c="dimmed">
                                        • Single JSON file containing all crew data
                                    </Text>
                                    <Text size="xs" c="dimmed">
                                        • Compact format, easy to version control
                                    </Text>
                                    <Text size="xs" c="dimmed">
                                        • Can be imported directly into any AI Crew Platform instance
                                    </Text>
                                </div>
                            ) : (
                                <div className="space-y-2">
                                    <Text size="xs" c="dimmed">
                                        • Organized folder structure with separate config files
                                    </Text>
                                    <Text size="xs" c="dimmed">
                                        • Includes README with setup instructions
                                    </Text>
                                    <Text size="xs" c="dimmed">
                                        • Better for sharing and documentation purposes
                                    </Text>
                                </div>
                            )}
                        </div>
                    </div>
                </Card>
            </Container>
        </div>
    );
}
