# Unified RevOps Dashboard with AI Co-Pilot
## Complete Implementation Specification

### Executive Summary

This specification outlines the development of a unified Revenue Operations (RevOps) dashboard with an integrated AI Co-Pilot for a B2B SaaS company. The dashboard consolidates marketing funnel analytics, sales pipeline management, financial/revenue tracking, and AI-powered insights into a cohesive platform built with modern web technologies.

**Key Features:**
- Four integrated views: Marketing, Sales Pipeline, Financial/Revenue, and AI Co-Pilot
- Real-time data processing with sub-second filter performance
- Cross-functional filtering and drill-down capabilities
- AI-powered insights and anomaly detection
- Accessible design following WCAG 2.2 standards
- Modern glassmorphism UI with dark mode default

### Technology Stack

**Frontend Framework:**
- Next.js 15 with App Router
- React 19 with Server Components
- TypeScript for type safety

**Styling & Components:**
- Tailwind CSS v4 with utility-first approach
- shadcn/ui component library (Radix primitives)
- Tremor charts for data visualization
- TanStack Table for data grids
- Vaul drawer for mobile interactions

**Performance & Data:**
- TanStack React Query for data fetching
- React Hook Form for form management
- Zod for schema validation
- CSV export functionality

### Data Model

#### Core Tables

**marketing_channels**
```sql
CREATE TABLE marketing_channels (
  date DATE,
  channel VARCHAR(50),
  campaign VARCHAR(100),
  segment ENUM('SMB', 'MM', 'ENT'),
  geo VARCHAR(10),
  spend DECIMAL(10,2),
  impressions INT,
  clicks INT,
  leads INT,
  MQLs INT,
  SQLs INT,
  opportunities INT,
  closed_won INT,
  CAC DECIMAL(8,2),
  CPL DECIMAL(6,2),
  CTR DECIMAL(6,4),
  CVR_stagewise DECIMAL(6,4),
  ROI DECIMAL(8,2)
);
```

**pipeline_deals**
```sql
CREATE TABLE pipeline_deals (
  deal_id VARCHAR(20) PRIMARY KEY,
  account VARCHAR(50),
  segment ENUM('SMB', 'MM', 'ENT'),
  owner VARCHAR(100),
  stage ENUM('Discovery', 'Demo', 'Negotiation', 'Closed_Won', 'Closed_Lost'),
  amount DECIMAL(12,2),
  created_at DATE,
  expected_close DATE,
  last_stage_change DATE,
  days_in_stage INT,
  probability DECIMAL(4,3),
  expected_value DECIMAL(12,2),
  status VARCHAR(20),
  source_channel VARCHAR(50)
);
```

**revenue_customers**
```sql
CREATE TABLE revenue_customers (
  customer_id VARCHAR(20) PRIMARY KEY,
  account VARCHAR(50),
  segment ENUM('SMB', 'MM', 'ENT'),
  plan VARCHAR(50),
  start_date DATE,
  mrr DECIMAL(10,2),
  new_mrr DECIMAL(10,2),
  expansion_mrr DECIMAL(10,2),
  contraction_mrr DECIMAL(10,2),
  churned_flag BOOLEAN,
  churn_date DATE,
  churn_reason VARCHAR(100),
  arpa DECIMAL(10,2),
  nrr DECIMAL(6,3)
);
```

**benchmarks**
```sql
CREATE TABLE benchmarks (
  benchmark_id VARCHAR(20) PRIMARY KEY,
  metric_type VARCHAR(50),
  category VARCHAR(50),
  subcategory VARCHAR(50),
  target_value DECIMAL(10,3),
  min_value DECIMAL(10,3),
  max_value DECIMAL(10,3),
  unit VARCHAR(20),
  description TEXT
);
```

### Key Metrics & Calculations

#### Marketing Metrics
```typescript
// Customer Acquisition Cost
const CAC = totalSpend / totalCustomersAcquired;

// Return on Investment
const ROI = (revenue - spend) / spend * 100;

// Conversion Rates by Stage
const leadToMQLRate = MQLs / leads;
const MQLToSQLRate = SQLs / MQLs;
const SQLToOpportunityRate = opportunities / SQLs;
```

#### Sales Metrics
```typescript
// Weighted Pipeline
const weightedPipeline = deals.reduce((sum, deal) => 
  sum + (deal.amount * deal.probability), 0
);

// Sales Velocity (per month)
const salesVelocity = (
  averageOpportunities * 
  averageDealValue * 
  winRate
) / averageSalesCycleDays * 30;

// Win Rate
const winRate = closedWonDeals / (closedWonDeals + closedLostDeals);
```

#### Revenue Metrics
```typescript
// Monthly Recurring Revenue Components
const totalMRR = newMRR + expansionMRR - contractionMRR - churnedMRR;

// Annual Recurring Revenue
const ARR = totalMRR * 12;

// Net Revenue Retention
const NRR = (startingMRR + expansionMRR - contractionMRR) / startingMRR;

// Customer Lifetime Value
const LTV = averageRevenuePerAccount / churnRate;

// LTV/CAC Ratio
const LTVCACRatio = LTV / CAC;
```

### Dashboard Views Specification

#### 1. Marketing Funnel View

**Layout Components:**
- Header with KPI cards (Spend, Leads, MQLs, SQLs, CAC, ROI)
- Main funnel visualization (Sankey diagram)
- Channel performance table with sorting/filtering
- Time-series charts for trend analysis
- Cohort analysis heatmap

**Interactive Features:**
```typescript
// Filter Configuration
interface MarketingFilters {
  dateRange: [Date, Date];
  channels: string[];
  campaigns: string[];
  segments: ('SMB' | 'MM' | 'ENT')[];
  geo: string[];
}

// Cross-filter Integration
const handleFilterChange = (filters: MarketingFilters) => {
  updatePipelineView(filters);
  updateRevenueView(filters);
  updateAICoPilot(filters);
};
```

**Key Visualizations:**
- Sankey funnel: Leads → MQL → SQL → Opportunity → Closed Won
- ROI leaderboard by channel
- Geographic performance map
- Campaign performance trends
- Lead quality cohort analysis

#### 2. Sales Pipeline View

**Layout Components:**
- Pipeline overview cards (Total, Weighted, Win Rate, Velocity)
- Stage-by-stage funnel visualization
- Rep performance leaderboard
- Deal health analysis table
- Time-in-stage distribution charts

**Key Features:**
```typescript
// Pipeline Health Scoring
interface DealHealth {
  dealId: string;
  healthScore: number; // 0-100
  riskFactors: string[];
  recommendations: string[];
}

// Velocity Calculation
const calculateVelocity = (segment: string) => {
  const deals = getDealsForSegment(segment);
  const avgDealValue = deals.reduce((sum, d) => sum + d.amount, 0) / deals.length;
  const avgCycleTime = deals.reduce((sum, d) => sum + d.cycleTime, 0) / deals.length;
  const winRate = deals.filter(d => d.stage === 'Closed_Won').length / deals.length;
  
  return (avgDealValue * winRate) / (avgCycleTime / 30); // Monthly velocity
};
```

#### 3. Financial/Revenue View

**Layout Components:**
- MRR waterfall chart (New, Expansion, Contraction, Churn)
- NRR trend line with variance indicators
- Churn analysis breakdown
- Customer segment revenue distribution
- CAC payback period gauges

**Key Visualizations:**
```typescript
// MRR Waterfall Data Structure
interface MRRWaterfall {
  period: string;
  startingMRR: number;
  newMRR: number;
  expansionMRR: number;
  contractionMRR: number;
  churnMRR: number;
  endingMRR: number;
}

// Cohort Retention Analysis
interface CohortData {
  cohortMonth: string;
  period0: number;
  period1: number;
  period2: number;
  // ... up to period12
}
```

#### 4. AI Co-Pilot Panel

**Conversation Interface:**
```typescript
interface AIMessage {
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

interface AIContext {
  currentView: 'marketing' | 'pipeline' | 'revenue';
  activeFilters: any;
  selectedDataPoints: any[];
  recentActions: string[];
}
```

**Supported Query Types:**
```typescript
const queryPatterns = {
  performance: /which (channel|rep|segment) (performed best|had highest|generated most)/i,
  comparison: /compare (.*) with (.*)/i,
  trends: /show (trend|pattern|growth) for (.*)/i,
  prediction: /predict|forecast|estimate/i,
  anomaly: /unusual|anomaly|outlier|strange/i,
  drill_down: /show details|break down|drill into/i
};

// AI Response Template
interface AIResponse {
  answer: string;
  confidence: number;
  dataSource: string[];
  suggestedActions: string[];
  chartRecommendation?: string;
  filterHighlights?: any;
}
```

### Component Architecture

#### Core Layout Structure
```typescript
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen bg-neutral-950">
      {/* Left Sidebar */}
      <DashboardSidebar />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <DashboardHeader />
        <main className="flex-1 overflow-hidden">
          {children}
        </main>
      </div>
      
      {/* AI Co-Pilot Drawer */}
  <AIDrawer />
    </div>
  );
}
```

#### Shared Components
```typescript
// components/ui/metric-card.tsx
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
}

// components/charts/tremor-wrapper.tsx
interface ChartWrapperProps {
  type: 'area' | 'bar' | 'line' | 'donut';
  data: any[];
  config: any;
  loading?: boolean;
  error?: string;
}

// components/filters/global-filter-bar.tsx
interface GlobalFilters {
  dateRange: DateRange;
  segment: string[];
  channel: string[];
  owner: string[];
  geo: string[];
}
```

### Performance Optimization

#### Data Loading Strategy
```typescript
// lib/data-fetching.ts
export const useMarketingData = (filters: MarketingFilters) => {
  return useQuery({
    queryKey: ['marketing', filters],
    queryFn: () => fetchMarketingData(filters),
    staleTime: 30 * 1000, // 30 seconds
    cacheTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Optimized aggregations
const getPreAggregatedData = (timeframe: string) => {
  // Pre-computed daily, weekly, monthly aggregates
  // Stored in separate tables for fast retrieval
};
```

#### Virtualization for Large Tables
```typescript
// components/tables/virtualized-table.tsx
import { useVirtualizer } from '@tanstack/react-virtual';

export function VirtualizedTable({ data, columns }: TableProps) {
  const virtualizer = useVirtualizer({
    count: data.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 10,
  });

  return (
    <div ref={parentRef} className="h-96 overflow-auto">
      {virtualizer.getVirtualItems().map((virtualRow) => (
        <TableRow
          key={virtualRow.index}
          data={data[virtualRow.index]}
          style={{
            height: `${virtualRow.size}px`,
            transform: `translateY(${virtualRow.start}px)`,
          }}
        />
      ))}
    </div>
  );
}
```

### Accessibility Implementation

#### WCAG 2.2 Compliance
```typescript
// Design system tokens
const accessibilityTokens = {
  contrast: {
    text: 'contrast-ratio: 4.5:1',
    ui: 'contrast-ratio: 3:1',
  },
  focus: {
    ring: 'ring-2 ring-blue-500 ring-offset-2',
    visible: 'focus-visible:outline-none',
  },
  motion: {
    reduced: '@media (prefers-reduced-motion: reduce)',
  },
};

// Keyboard navigation
const useKeyboardNavigation = () => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'Tab':
          // Handle focus management
          break;
        case 'Enter':
        case ' ':
          // Activate focused element
          break;
        case 'Escape':
          // Close modals/drawers
          break;
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);
};
```

#### Screen Reader Support
```typescript
// components/charts/accessible-chart.tsx
export function AccessibleChart({ data, type, title, description }: ChartProps) {
  return (
    <div role="img" aria-labelledby={`chart-title-${id}`} aria-describedby={`chart-desc-${id}`}>
      <h3 id={`chart-title-${id}`} className="sr-only">{title}</h3>
      <p id={`chart-desc-${id}`} className="sr-only">{description}</p>
      
      {/* Visual chart */}
      <TremorChart {...chartProps} />
      
      {/* Screen reader table alternative */}
      <table className="sr-only">
        <caption>{title}: {description}</caption>
        {/* Data table representation */}
      </table>
    </div>
  );
}
```

### AI Co-Pilot Implementation

#### Natural Language Processing
```typescript
// lib/ai/query-processor.ts
export class QueryProcessor {
  private intentClassifier: IntentClassifier;
  private entityExtractor: EntityExtractor;
  private responseGenerator: ResponseGenerator;

  async processQuery(query: string, context: AIContext): Promise<AIResponse> {
    // 1. Intent classification
    const intent = await this.intentClassifier.classify(query);
    
    // 2. Entity extraction
    const entities = await this.entityExtractor.extract(query);
    
    // 3. Data retrieval
    const data = await this.retrieveData(entities, context);
    
    // 4. Response generation
    const response = await this.responseGenerator.generate({
      intent,
      entities,
      data,
      context
    });
    
    return response;
  }
}
```

#### Data Retrieval Engine
```typescript
// lib/ai/data-engine.ts
interface DataQuery {
  metrics: string[];
  dimensions: string[];
  filters: Record<string, any>;
  timeRange: [Date, Date];
  aggregation?: 'sum' | 'avg' | 'count' | 'min' | 'max';
}

export class DataEngine {
  async executeQuery(query: DataQuery): Promise<any[]> {
    // Convert natural language query to SQL/API calls
    const sqlQuery = this.buildQuery(query);
    return await this.database.execute(sqlQuery);
  }
  
  private buildQuery(query: DataQuery): string {
    // Dynamic SQL generation based on query parameters
    // Includes security measures to prevent injection
  }
}
```

### Testing Strategy

#### Unit Tests
```typescript
// __tests__/components/metric-card.test.tsx
describe('MetricCard', () => {
  it('displays metric value correctly', () => {
    render(<MetricCard title="MRR" value={50000} format="currency" />);
    expect(screen.getByText('$50,000')).toBeInTheDocument();
  });

  it('shows positive change indicator', () => {
    const change = { value: 15.5, type: 'positive' as const, period: 'MoM' };
    render(<MetricCard title="ARR" value={600000} change={change} />);
    expect(screen.getByText('↗ 15.5%')).toBeInTheDocument();
  });
});
```

#### Integration Tests
```typescript
// __tests__/integration/dashboard-flow.test.tsx
describe('Dashboard Integration', () => {
  it('applies cross-filters across all views', async () => {
    render(<Dashboard />);
    
    // Apply filter in marketing view
    fireEvent.click(screen.getByText('Google Ads'));
    
    // Verify filter applied to pipeline view
    await waitFor(() => {
      expect(screen.getByTestId('pipeline-deals')).toHaveAttribute(
        'data-filtered-by', 'Google Ads'
      );
    });
  });
});
```

### Deployment Configuration

#### Next.js Configuration
```typescript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
    serverComponentsExternalPackages: ['@tremor/react'],
  },
  images: {
    domains: ['cdn.example.com'],
  },
  async rewrites() {
    return [
      {
        source: '/api/data/:path*',
        destination: `${process.env.API_BASE_URL}/api/data/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
```

#### Environment Variables
```bash
# .env.local
DATABASE_URL="postgresql://username:password@localhost:5432/revops_db"
API_BASE_URL="https://api.revops.company.com"

REDIS_URL="redis://localhost:6379"
NODE_ENV="development"
```

### Security Considerations

#### Data Protection
```typescript
// lib/security/data-access.ts
export class DataAccessControl {
  private userPermissions: Map<string, Permission[]>;
  
  async validateAccess(userId: string, resource: string, action: string): Promise<boolean> {
    const permissions = await this.getUserPermissions(userId);
    return permissions.some(p => p.resource === resource && p.actions.includes(action));
  }
  
  async filterSensitiveData(data: any[], userId: string): Promise<any[]> {
    const userRole = await this.getUserRole(userId);
    
    if (userRole === 'viewer') {
      // Remove sensitive fields
      return data.map(item => omit(item, ['individual_performance', 'salary_data']));
    }
    
    return data;
  }
}
```

### Maintenance & Monitoring

#### Performance Monitoring
```typescript
// lib/monitoring/performance.ts
export const trackPageLoad = (pageName: string, loadTime: number) => {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', 'page_view_timing', {
      custom_parameter_1: pageName,
      value: Math.round(loadTime),
    });
  }
};

// Error tracking
export const trackError = (error: Error, context: any) => {
  console.error('Dashboard Error:', error, context);
  
  // Send to error tracking service
  if (process.env.NODE_ENV === 'production') {
    errorTrackingService.captureException(error, { extra: context });
  }
};
```

### Conclusion

This specification provides a comprehensive foundation for building a production-ready RevOps dashboard with AI capabilities. The modular architecture, performance optimizations, and accessibility features ensure the dashboard will scale effectively while providing an excellent user experience across all stakeholder groups.

**Next Steps:**
1. Set up development environment and install dependencies
2. Implement core data models and API endpoints
3. Build shared component library with design system
4. Develop each dashboard view incrementally
5. Integrate AI Co-Pilot functionality
6. Conduct comprehensive testing and accessibility audits
7. Deploy to staging environment for user acceptance testing
8. Production deployment with monitoring and analytics

---

*This specification serves as a living document and should be updated as requirements evolve and new features are identified.*