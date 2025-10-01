from pathlib import Path


def write_mermaid_diagram(diagram: str, name: str) -> Path:
    output_path = Path(name).with_suffix(".mmd")
    output_path.write_text(diagram)
    print(f"Mermaid source saved to {output_path}")
    print("Use Mermaid CLI (mmdc) to render PNG/SVG if desired.")
    return output_path


diagram_code = """
flowchart TD
    %% Technology Stack
    Tech["Tech Stack<br/>Next.js 15 | React 19<br/>Tailwind CSS v4 | shadcn/ui<br/>Tremor | TanStack Table"]
    
    %% Main Dashboard Views
    Marketing["Marketing Funnel<br/>View"]
    Sales["Sales Pipeline<br/>View"] 
    Financial["Financial/Revenue<br/>View"]
        InsightsView["Insights<br/>View"]
    
    %% Data Processing Layer
    API["API Layer"]
    DataProc["Data Processing"]
    Metrics["Metrics Engine"]
    AIEngine["AI Engine"]
    
    %% Database Tables
    MarketingDB["marketing_channels<br/>Table"]
    PipelineDB["pipeline_deals<br/>Table"]
    RevenueDB["revenue_customers<br/>Table"]
    BenchmarkDB["benchmarks<br/>Table"]
    
    %% Technology Stack to Views
    Tech --> Marketing
    Tech --> Sales
    Tech --> Financial
        Tech --> InsightsView
    
    %% Views to Processing Layer
    Marketing --> API
    Sales --> API
    Financial --> API
        InsightsView --> InsightsEngine
    
    %% Processing Layer Connections
    API --> DataProc
    DataProc --> Metrics
        InsightsEngine --> Metrics
    
    %% Data Tables to Processing
    MarketingDB --> DataProc
    PipelineDB --> DataProc
    RevenueDB --> DataProc
    BenchmarkDB --> Metrics
"""

write_mermaid_diagram(diagram_code, "revops_architecture")