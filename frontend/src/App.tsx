import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

function Dashboard() {
  return (
    <div className="min-h-screen bg-[var(--bg-base)] text-[var(--text-primary)] font-sans p-6">
      <h1 className="text-2xl font-bold">Stock Sentiment Tracker</h1>
      <p className="text-sm text-[var(--text-secondary)] mt-2">
        Frontend scaffolded. Next step: build dashboard components per production guide.
      </p>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard />
      <Toaster position="bottom-right" />
    </QueryClientProvider>
  );
}

