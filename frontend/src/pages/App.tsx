import type { ReactNode } from 'react';
import { CssBaseline, Typography } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';

const queryClient = new QueryClient();

export function App() {
  return (
    <StrictModeProviders>
      <main aria-label="TTX Trader application shell" style={{ padding: 24 }}>
        <Typography variant="h3" component="h1">
          Taiwan Tradovate (TTX Trader)
        </Typography>
        <Typography variant="body1">
          Phase 1 project foundation is ready for TAIFEX trading workflows.
        </Typography>
      </main>
    </StrictModeProviders>
  );
}

function StrictModeProviders({ children }: { children: ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <CssBaseline />
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
}
