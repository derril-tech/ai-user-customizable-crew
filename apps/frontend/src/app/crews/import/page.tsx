'use client';

import { useState } from 'react';
import { Container, Title, Card, Button, Group, Text, FileInput, Switch, TextInput, Alert } from '@mantine/core';
import { Upload, FileText, ArrowLeft, CheckCircle } from 'lucide-react';
import Link from 'next/link';
import { useMutation } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';

export default function CrewImportPage() {
    const [file, setFile] = useState<File | null>(null);
    const [importAsTemplate, setImportAsTemplate] = useState(false);
    const [overrideName, setOverrideName] = useState('');
    const [importedCrew, setImportedCrew] = useState<any>(null);

    const importMutation = useMutation({
        mutationFn: async (formData: FormData) => {
            const response = await fetch('/api/v1/export/import/file', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Import failed');
            }

            return response.json();
        },
        onSuccess: (data) => {
            setImportedCrew(data);
            notifications.show({
                title: 'Success',
                message: 'Crew imported successfully!',
                color: 'green',
            });
        },
        onError: (error: Error) => {
            notifications.show({
                title: 'Import Failed',
                message: error.message,
                color: 'red',
            });
        },
    });

    const handleImport = async () => {
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);
        formData.append('import_as_template', importAsTemplate.toString());
        if (overrideName) {
            formData.append('override_name', overrideName);
        }

        importMutation.mutate(formData);
    };

    const handleFileChange = (selectedFile: File | null) => {
        setFile(selectedFile);
        setImportedCrew(null); // Reset imported crew when new file is selected
    };

    if (importedCrew) {
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
                            <Title order={2}>Import Complete</Title>
                        </Group>
                    </Container>
                </header>

                <Container size="md" className="py-8">
                    <Card shadow="sm" padding="xl" radius="md" withBorder className="text-center">
                        <CheckCircle size={64} className="mx-auto mb-4 text-green-500" />
                        <Title order={3} className="mb-2">Crew Imported Successfully!</Title>
                        <Text className="mb-6 text-gray-600">
                            "{importedCrew.name}" has been imported and is ready to use.
                        </Text>

                        <Group justify="center">
                            <Link href={`/crews/${importedCrew.id}`}>
                                <Button>View Crew</Button>
                            </Link>
                            <Link href="/crews">
                                <Button variant="outline">All Crews</Button>
                            </Link>
                            <Button
                                variant="subtle"
                                onClick={() => {
                                    setImportedCrew(null);
                                    setFile(null);
                                }}
                            >
                                Import Another
                            </Button>
                        </Group>
                    </Card>
                </Container>
            </div>
        );
    }

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
                        <Title order={2}>Import Crew</Title>
                    </Group>
                </Container>
            </header>

            <Container size="md" className="py-8">
                <Card shadow="sm" padding="xl" radius="md" withBorder>
                    <div className="mb-6">
                        <Title order={3} className="mb-2">Import Crew Configuration</Title>
                        <Text className="text-gray-600">
                            Upload a crew configuration file (JSON or ZIP) to import an existing crew setup.
                        </Text>
                    </div>

                    <div className="space-y-6">
                        {/* File Upload */}
                        <div>
                            <Text size="sm" fw={500} className="mb-2">Select File</Text>
                            <FileInput
                                placeholder="Choose JSON or ZIP file"
                                accept=".json,.zip"
                                value={file}
                                onChange={handleFileChange}
                                leftSection={<Upload size={16} />}
                            />
                            <Text size="xs" c="dimmed" className="mt-1">
                                Supported formats: JSON (single file) or ZIP (organized export)
                            </Text>
                        </div>

                        {/* Import Options */}
                        <div>
                            <Text size="sm" fw={500} className="mb-3">Import Options</Text>

                            <div className="space-y-3">
                                <Group justify="space-between" className="p-3 bg-gray-50 rounded">
                                    <div>
                                        <Text size="sm" fw={500}>Import as Template</Text>
                                        <Text size="xs" c="dimmed">
                                            Make this crew available as a template for others to use
                                        </Text>
                                    </div>
                                    <Switch
                                        checked={importAsTemplate}
                                        onChange={(event) => setImportAsTemplate(event.currentTarget.checked)}
                                    />
                                </Group>

                                <TextInput
                                    label="Override Name (Optional)"
                                    placeholder="Enter new name for the crew"
                                    value={overrideName}
                                    onChange={(event) => setOverrideName(event.currentTarget.value)}
                                    description="Leave empty to use the original name from the export"
                                />
                            </div>
                        </div>

                        {/* File Info */}
                        {file && (
                            <Alert color="blue" icon={<FileText size={16} />}>
                                <Text size="sm" fw={500} className="mb-1">File Selected</Text>
                                <Text size="xs">
                                    Name: {file.name}<br />
                                    Size: {(file.size / 1024).toFixed(1)} KB<br />
                                    Type: {file.type || 'Unknown'}
                                </Text>
                            </Alert>
                        )}

                        {/* Import Button */}
                        <Group justify="center" className="pt-4">
                            <Button
                                size="lg"
                                leftSection={<Upload size={20} />}
                                onClick={handleImport}
                                disabled={!file}
                                loading={importMutation.isPending}
                            >
                                {importMutation.isPending ? 'Importing...' : 'Import Crew'}
                            </Button>
                        </Group>

                        {/* Instructions */}
                        <div className="pt-6 border-t">
                            <Text size="sm" fw={500} className="mb-2">Import Instructions</Text>

                            <div className="space-y-2">
                                <Text size="xs" c="dimmed">
                                    1. Select a crew export file (JSON or ZIP format)
                                </Text>
                                <Text size="xs" c="dimmed">
                                    2. Choose whether to import as a template
                                </Text>
                                <Text size="xs" c="dimmed">
                                    3. Optionally override the crew name
                                </Text>
                                <Text size="xs" c="dimmed">
                                    4. Click "Import Crew" to complete the process
                                </Text>
                            </div>

                            <Alert color="yellow" className="mt-4">
                                <Text size="xs">
                                    <strong>Note:</strong> Imported crews will be assigned to your organization.
                                    Make sure you have the necessary permissions to create new crews.
                                </Text>
                            </Alert>
                        </div>
                    </div>
                </Card>
            </Container>
        </div>
    );
}
