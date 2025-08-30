import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import { ModalsProvider } from '@mantine/modals';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
    title: 'AI Crew Platform',
    description: 'User-customizable AI crew orchestration platform',
};

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 5 * 60 * 1000, // 5 minutes
            retry: 1,
        },
    },
});

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <QueryClientProvider client={queryClient}>
                    <MantineProvider>
                        <ModalsProvider>
                            <Notifications />
                            {children}
                            <ReactQueryDevtools initialIsOpen={false} />
                        </ModalsProvider>
                    </MantineProvider>
                </QueryClientProvider>
            </body>
        </html>
    );
}
