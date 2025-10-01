# RevOps Dashboard - Code Scaffolding

## Project Structure

```
revops-dashboard/
├── app/
│   ├── dashboard/
│   │   ├── marketing/
│   │   │   └── page.tsx
│   │   ├── pipeline/
│   │   │   └── page.tsx
│   │   ├── revenue/
│   │   │   └── page.tsx
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── api/
│   │   ├── marketing/
│   │   ├── pipeline/
│   │   ├── revenue/
│   │   └── ai/
│   ├── globals.css
│   └── layout.tsx
├── components/
│   ├── ui/
│   │   ├── card.tsx
│   │   ├── button.tsx
│   │   ├── table.tsx
│   │   └── chart.tsx
│   ├── dashboard/
│   │   ├── sidebar.tsx
│   │   ├── header.tsx
│   │   ├── filters/
│   │   ├── charts/
│   │   └── tables/
│   └── ai/
│       ├── copilot-drawer.tsx
│       ├── chat-interface.tsx
│       └── query-processor.tsx
├── lib/
│   ├── data/
│   ├── ai/
│   ├── utils.ts
│   └── types.ts
├── data/
│   ├── marketing_channels.csv
│   ├── pipeline_deals.csv
│   ├── revenue_customers.csv
│   └── benchmarks.csv
└── package.json
```

## Core Dependencies

```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@tanstack/react-table": "^8.11.0",
    "@tanstack/react-query": "^5.15.0",
    "@tremor/react": "^3.13.0",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-select": "^2.0.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0",
    "lucide-react": "^0.292.0",
    "date-fns": "^2.30.0",
    "recharts": "^2.8.0",
    "vaul": "^0.9.0",
    "react-hook-form": "^7.48.0",
    "@hookform/resolvers": "^3.3.0",
    "zod": "^3.22.0"
  },
  "devDependencies": {
    "@types/node": "^20.9.0",
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "typescript": "^5.2.2",
    "tailwindcss": "^4.0.0-alpha.1",
    "eslint": "^8.53.0",
    "eslint-config-next": "^14.0.3"
  }
}
```

## Key Component Implementations

### Dashboard Layout

```typescript
// app/dashboard/layout.tsx
import { DashboardSidebar } from '@/components/dashboard/sidebar';
import { DashboardHeader } from '@/components/dashboard/header';
import { AICopilotDrawer } from '@/components/ai/copilot-drawer';
import { GlobalFiltersProvider } from '@/lib/contexts/global-filters';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <GlobalFiltersProvider>
      <div className="flex h-screen bg-neutral-950 text-neutral-50">
        <DashboardSidebar />
        <div className="flex-1 flex flex-col">
          <DashboardHeader />
          <main className="flex-1 overflow-hidden p-6">
            {children}
          </main>
        </div>
        <AICopilotDrawer />
      </div>
    </GlobalFiltersProvider>
  );
}
```

### Global Filter Provider

```typescript
// lib/contexts/global-filters.tsx
'use client';

import { createContext, useContext, useState, useCallback } from 'react';
import { DateRange } from 'react-day-picker';

interface GlobalFilters {
  dateRange: DateRange | undefined;
  segments: string[];
  channels: string[];
  owners: string[];
  geo: string[];
}

interface GlobalFiltersContextType {
  filters: GlobalFilters;
  updateFilters: (updates: Partial<GlobalFilters>) => void;
  clearFilters: () => void;
}

const GlobalFiltersContext = createContext<GlobalFiltersContextType | null>(null);

export function GlobalFiltersProvider({ children }: { children: React.ReactNode }) {
  const [filters, setFilters] = useState<GlobalFilters>({
    dateRange: undefined,
    segments: [],
    channels: [],
    owners: [],
    geo: [],
  });

  const updateFilters = useCallback((updates: Partial<GlobalFilters>) => {
    setFilters(prev => ({ ...prev, ...updates }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({
      dateRange: undefined,
      segments: [],
      channels: [],
      owners: [],
      geo: [],
    });
  }, []);

  return (
    <GlobalFiltersContext.Provider value={{ filters, updateFilters, clearFilters }}>
      {children}
    </GlobalFiltersContext.Provider>
  );
}

export const useGlobalFilters = () => {
  const context = useContext(GlobalFiltersContext);
  if (!context) {
    throw new Error('useGlobalFilters must be used within a GlobalFiltersProvider');
  }
  return context;
};
```

### Metric Card Component

```typescript
// components/ui/metric-card.tsx
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: {
    value: number;
    type: 'positive' | 'negative' | 'neutral';
    period: string;
  };
  benchmark?: {
    target: number;
    current: number;
  };
  format?: 'currency' | 'percentage' | 'number';
  loading?: boolean;
}

export function MetricCard({
  title,
  value,
  change,
  benchmark,
  format = 'number',
  loading = false
}: MetricCardProps) {
  const formatValue = (val: string | number) => {
    if (loading) return '---';
    
    if (typeof val === 'string') return val;
    
    switch (format) {
      case 'currency':
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
          minimumFractionDigits: 0,
          maximumFractionDigits: 0,
        }).format(val);
      case 'percentage':
        return `${val.toFixed(1)}%`;
      default:
        return val.toLocaleString();
    }
  };

  const getTrendIcon = (type: 'positive' | 'negative' | 'neutral') => {
    switch (type) {
      case 'positive':
        return <TrendingUp className="w-4 h-4" />;
      case 'negative':
        return <TrendingDown className="w-4 h-4" />;
      default:
        return <Minus className="w-4 h-4" />;
    }
  };

  const getTrendColor = (type: 'positive' | 'negative' | 'neutral') => {
    switch (type) {
      case 'positive':
        return 'text-green-500 bg-green-500/10';
      case 'negative':
        return 'text-red-500 bg-red-500/10';
      default:
        return 'text-neutral-500 bg-neutral-500/10';
    }
  };

  return (
    <Card className="bg-neutral-900/50 border-neutral-800 backdrop-blur-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-neutral-400">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-end justify-between">
          <div>
            <div className="text-2xl font-bold text-neutral-50">
              {formatValue(value)}
            </div>
            {change && (
              <div className={cn(
                "flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full mt-2 w-fit",
                getTrendColor(change.type)
              )}>
                {getTrendIcon(change.type)}
                <span>{Math.abs(change.value).toFixed(1)}%</span>
                <span className="text-neutral-400">{change.period}</span>
              </div>
            )}
          </div>
          {benchmark && (
            <div className="text-right">
              <div className="text-xs text-neutral-400">Target</div>
              <div className="text-sm font-medium">
                {formatValue(benchmark.target)}
              </div>
              <Badge 
                variant={benchmark.current >= benchmark.target ? 'default' : 'destructive'}
                className="text-xs"
              >
                {benchmark.current >= benchmark.target ? 'On Track' : 'Below Target'}
              </Badge>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
```

### Data Fetching Hook

```typescript
// lib/hooks/use-marketing-data.ts
import { useQuery } from '@tanstack/react-query';
import { useGlobalFilters } from '@/lib/contexts/global-filters';

interface MarketingDataParams {
  dateRange?: { from: Date; to: Date };
  segments?: string[];
  channels?: string[];
  geo?: string[];
}

export function useMarketingData() {
  const { filters } = useGlobalFilters();
  
  return useQuery({
    queryKey: ['marketing-data', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      
      if (filters.dateRange?.from) {
        params.append('startDate', filters.dateRange.from.toISOString());
      }
      if (filters.dateRange?.to) {
        params.append('endDate', filters.dateRange.to.toISOString());
      }
      if (filters.segments.length > 0) {
        params.append('segments', filters.segments.join(','));
      }
      if (filters.channels.length > 0) {
        params.append('channels', filters.channels.join(','));
      }
      if (filters.geo.length > 0) {
        params.append('geo', filters.geo.join(','));
      }

      const response = await fetch(`/api/marketing?${params.toString()}`);
      if (!response.ok) {
        throw new Error('Failed to fetch marketing data');
      }
      
      return response.json();
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
  });
}
```

### AI Co-Pilot Component

```typescript
// components/ai/copilot-drawer.tsx
'use client';

import { useState } from 'react';
import { Drawer } from 'vaul';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { MessageSquare, Send, Sparkles, X } from 'lucide-react';
import { ChatInterface } from './chat-interface';
import { useGlobalFilters } from '@/lib/contexts/global-filters';

export function AICopilotDrawer() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<AIMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hi! I can help you analyze your RevOps data. Try asking me about channel performance, pipeline health, or churn predictions.',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { filters } = useGlobalFilters();

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: AIMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/ai/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: inputValue,
          context: {
            filters,
            currentView: 'dashboard',
            timestamp: new Date().toISOString(),
          },
        }),
      });

      const aiResponse = await response.json();

      const assistantMessage: AIMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: aiResponse.answer,
        timestamp: new Date(),
        attachments: aiResponse.attachments,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('AI query failed:', error);
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date(),
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsOpen(true)}
        className="fixed top-4 right-4 z-50 bg-neutral-900/80 border-neutral-700 backdrop-blur-sm hover:bg-neutral-800/80"
      >
        <Sparkles className="w-4 h-4 mr-2" />
        AI Co-Pilot
      </Button>

      <Drawer.Root open={isOpen} onOpenChange={setIsOpen} direction="right">
        <Drawer.Portal>
          <Drawer.Overlay className="fixed inset-0 bg-black/40 z-40" />
          <Drawer.Content className="bg-neutral-950 flex flex-col rounded-l-[10px] h-full w-[400px] fixed bottom-0 right-0 z-50 border-l border-neutral-800">
            <div className="flex items-center justify-between p-4 border-b border-neutral-800">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-blue-500" />
                <h2 className="text-lg font-semibold">AI Co-Pilot</h2>
                <Badge variant="secondary" className="text-xs">
                  Beta
                </Badge>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsOpen(false)}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>

            <div className="flex-1 overflow-hidden">
              <ChatInterface
                messages={messages}
                isLoading={isLoading}
              />
            </div>

            <div className="p-4 border-t border-neutral-800">
              <div className="flex gap-2">
                <Input
                  placeholder="Ask me anything about your RevOps data..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                  disabled={isLoading}
                  className="flex-1 bg-neutral-900 border-neutral-700"
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  size="sm"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </Drawer.Content>
        </Drawer.Portal>
      </Drawer.Root>
    </>
  );
}
```

### Marketing View Page

```typescript
// app/dashboard/marketing/page.tsx
'use client';

import { MetricCard } from '@/components/ui/metric-card';
import { Card } from '@/components/ui/card';
import { AreaChart, BarChart, DonutChart } from '@tremor/react';
import { DataTable } from '@/components/ui/data-table';
import { useMarketingData } from '@/lib/hooks/use-marketing-data';
import { GlobalFilters } from '@/components/dashboard/global-filters';

export default function MarketingPage() {
  const { data: marketingData, isLoading, error } = useMarketingData();

  if (error) {
    return <div className="p-8 text-red-500">Error loading marketing data</div>;
  }

  const metrics = marketingData?.metrics || {
    totalSpend: 0,
    totalLeads: 0,
    totalMQLs: 0,
    totalSQLs: 0,
    avgCAC: 0,
    avgROI: 0,
  };

  const channelPerformance = marketingData?.channelPerformance || [];
  const funnelData = marketingData?.funnelData || [];
  const trendsData = marketingData?.trendsData || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Marketing Funnel</h1>
        <GlobalFilters />
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <MetricCard
          title="Total Spend"
          value={metrics.totalSpend}
          format="currency"
          loading={isLoading}
          change={{
            value: 12.5,
            type: 'positive',
            period: 'MoM'
          }}
        />
        <MetricCard
          title="Total Leads"
          value={metrics.totalLeads}
          loading={isLoading}
          change={{
            value: 8.2,
            type: 'positive',
            period: 'MoM'
          }}
        />
        <MetricCard
          title="MQLs"
          value={metrics.totalMQLs}
          loading={isLoading}
          change={{
            value: -2.1,
            type: 'negative',
            period: 'MoM'
          }}
        />
        <MetricCard
          title="SQLs"
          value={metrics.totalSQLs}
          loading={isLoading}
          change={{
            value: 15.7,
            type: 'positive',
            period: 'MoM'
          }}
        />
        <MetricCard
          title="Average CAC"
          value={metrics.avgCAC}
          format="currency"
          loading={isLoading}
          benchmark={{
            target: 200,
            current: metrics.avgCAC
          }}
        />
        <MetricCard
          title="Average ROI"
          value={metrics.avgROI}
          format="percentage"
          loading={isLoading}
          benchmark={{
            target: 400,
            current: metrics.avgROI
          }}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6 bg-neutral-900/50 border-neutral-800 backdrop-blur-sm">
          <h3 className="text-lg font-semibold mb-4">Marketing Funnel</h3>
          <BarChart
            data={funnelData}
            index="stage"
            categories={["count"]}
            colors={["blue"]}
            yAxisWidth={60}
            className="h-80"
          />
        </Card>

        <Card className="p-6 bg-neutral-900/50 border-neutral-800 backdrop-blur-sm">
          <h3 className="text-lg font-semibold mb-4">Channel Performance</h3>
          <DonutChart
            data={channelPerformance}
            category="spend"
            index="channel"
            colors={["blue", "green", "yellow", "red", "purple"]}
            className="h-80"
          />
        </Card>
      </div>

      {/* Trends Chart */}
      <Card className="p-6 bg-neutral-900/50 border-neutral-800 backdrop-blur-sm">
        <h3 className="text-lg font-semibold mb-4">Performance Trends</h3>
        <AreaChart
          data={trendsData}
          index="date"
          categories={["leads", "MQLs", "SQLs"]}
          colors={["blue", "green", "yellow"]}
          yAxisWidth={60}
          className="h-80"
        />
      </Card>

      {/* Channel Performance Table */}
      <Card className="p-6 bg-neutral-900/50 border-neutral-800 backdrop-blur-sm">
        <h3 className="text-lg font-semibold mb-4">Channel Details</h3>
        <DataTable
          data={channelPerformance}
          columns={[
            { accessorKey: 'channel', header: 'Channel' },
            { accessorKey: 'spend', header: 'Spend', cell: (info) => `$${info.getValue().toLocaleString()}` },
            { accessorKey: 'leads', header: 'Leads' },
            { accessorKey: 'MQLs', header: 'MQLs' },
            { accessorKey: 'CAC', header: 'CAC', cell: (info) => `$${info.getValue()}` },
            { accessorKey: 'ROI', header: 'ROI', cell: (info) => `${info.getValue()}%` },
          ]}
        />
      </Card>
    </div>
  );
}
```

### API Route Example

```typescript
// app/api/marketing/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { parseISO, isWithinInterval } from 'date-fns';
import marketingData from '@/data/marketing_channels.csv';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  
  const startDate = searchParams.get('startDate');
  const endDate = searchParams.get('endDate');
  const segments = searchParams.get('segments')?.split(',') || [];
  const channels = searchParams.get('channels')?.split(',') || [];
  const geo = searchParams.get('geo')?.split(',') || [];

  try {
    let filteredData = [...marketingData];

    // Apply date filter
    if (startDate && endDate) {
      const start = parseISO(startDate);
      const end = parseISO(endDate);
      filteredData = filteredData.filter(row => 
        isWithinInterval(parseISO(row.date), { start, end })
      );
    }

    // Apply segment filter
    if (segments.length > 0) {
      filteredData = filteredData.filter(row => segments.includes(row.segment));
    }

    // Apply channel filter
    if (channels.length > 0) {
      filteredData = filteredData.filter(row => channels.includes(row.channel));
    }

    // Apply geo filter
    if (geo.length > 0) {
      filteredData = filteredData.filter(row => geo.includes(row.geo));
    }

    // Calculate aggregated metrics
    const metrics = {
      totalSpend: filteredData.reduce((sum, row) => sum + parseFloat(row.spend), 0),
      totalLeads: filteredData.reduce((sum, row) => sum + parseInt(row.leads), 0),
      totalMQLs: filteredData.reduce((sum, row) => sum + parseInt(row.MQLs), 0),
      totalSQLs: filteredData.reduce((sum, row) => sum + parseInt(row.SQLs), 0),
      avgCAC: filteredData.reduce((sum, row) => sum + parseFloat(row.CAC), 0) / filteredData.length,
      avgROI: filteredData.reduce((sum, row) => sum + parseFloat(row.ROI), 0) / filteredData.length,
    };

    // Channel performance aggregation
    const channelPerformance = Array.from(
      filteredData.reduce((acc, row) => {
        const channel = row.channel;
        if (!acc.has(channel)) {
          acc.set(channel, { channel, spend: 0, leads: 0, MQLs: 0, CAC: 0, ROI: 0, count: 0 });
        }
        const data = acc.get(channel)!;
        data.spend += parseFloat(row.spend);
        data.leads += parseInt(row.leads);
        data.MQLs += parseInt(row.MQLs);
        data.CAC += parseFloat(row.CAC);
        data.ROI += parseFloat(row.ROI);
        data.count += 1;
        return acc;
      }, new Map())
    ).map(([_, data]) => ({
      ...data,
      CAC: data.CAC / data.count,
      ROI: data.ROI / data.count,
    }));

    return NextResponse.json({
      metrics,
      channelPerformance,
      funnelData: [
        { stage: 'Leads', count: metrics.totalLeads },
        { stage: 'MQLs', count: metrics.totalMQLs },
        { stage: 'SQLs', count: metrics.totalSQLs },
      ],
      trendsData: [] // Would implement time-series aggregation
    });
  } catch (error) {
    console.error('Marketing API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch marketing data' },
      { status: 500 }
    );
  }
}
```

### Types Definition

```typescript
// lib/types.ts
export interface AIMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  attachments?: {
    chartId?: string;
    tableData?: any[];
    filters?: any;
  };
}

export interface GlobalFilters {
  dateRange?: { from: Date; to: Date };
  segments: string[];
  channels: string[];
  owners: string[];
  geo: string[];
}

export interface MetricData {
  value: number;
  change?: {
    value: number;
    type: 'positive' | 'negative' | 'neutral';
    period: string;
  };
  benchmark?: {
    target: number;
    current: number;
  };
}

export interface MarketingData {
  date: string;
  channel: string;
  campaign: string;
  segment: 'SMB' | 'MM' | 'ENT';
  geo: string;
  spend: number;
  impressions: number;
  clicks: number;
  leads: number;
  MQLs: number;
  SQLs: number;
  opportunities: number;
  closed_won: number;
  CAC: number;
  CPL: number;
  CTR: number;
  CVR_stagewise: number;
  ROI: number;
}

export interface PipelineData {
  deal_id: string;
  account: string;
  segment: 'SMB' | 'MM' | 'ENT';
  owner: string;
  stage: 'Discovery' | 'Demo' | 'Negotiation' | 'Closed_Won' | 'Closed_Lost';
  amount: number;
  created_at: string;
  expected_close: string;
  last_stage_change: string;
  days_in_stage: number;
  probability: number;
  expected_value: number;
  status: string;
  source_channel: string;
}

export interface RevenueData {
  customer_id: string;
  account: string;
  segment: 'SMB' | 'MM' | 'ENT';
  plan: string;
  start_date: string;
  mrr: number;
  new_mrr: number;
  expansion_mrr: number;
  contraction_mrr: number;
  churned_flag: boolean;
  churn_date: string | null;
  churn_reason: string | null;
  arpa: number;
  nrr: number;
}
```

---

## Quick Start Guide

### 1. Project Setup

```bash
npx create-next-app@latest revops-dashboard --typescript --tailwind --eslint --app
cd revops-dashboard
npm install @tanstack/react-table @tanstack/react-query @tremor/react @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-select class-variance-authority clsx tailwind-merge lucide-react date-fns recharts vaul react-hook-form @hookform/resolvers zod
```

### 2. Environment Setup

```bash
# .env.local
NEXT_PUBLIC_APP_URL=http://localhost:3000
DATABASE_URL=your_database_url_here

```

### 3. Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './node_modules/@tremor/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
      },
    },
  },
  plugins: [],
};
```

### 4. Data Setup

```bash
# Copy provided CSV files to data/ directory
mkdir data
cp marketing_channels.csv pipeline_deals.csv revenue_customers.csv benchmarks.csv data/
```

### 5. Run Development Server

```bash
npm run dev
```

Navigate to `http://localhost:3000/dashboard` to see the application.

---

This scaffolding provides the foundation for building the complete RevOps dashboard. Each component can be expanded with additional features, styling, and functionality based on specific requirements.