from pathlib import Path


def write_mermaid_diagram(diagram: str, name: str) -> Path:
    output_path = Path(name).with_suffix(".mmd")
    output_path.write_text(diagram)
    print(f"Mermaid source saved to {output_path}")
    print("Render PNG/SVG via Mermaid CLI (mmdc) if available.")
    return output_path


diagram_code = '''
erDiagram
    marketing_channels {
        date date
        channel string
        campaign string
        segment string
        geo string
        spend decimal
        impressions int
        clicks int
        leads int
        MQLs int
        SQLs int
        opportunities int
        closed_won int
        CAC decimal
        CPL decimal
        CTR decimal
        CVR_stagewise decimal
        ROI decimal
    }
    
    pipeline_deals {
        deal_id string PK
        account string
        segment string
        owner string
        stage string
        amount decimal
        created_at date
        expected_close date
        last_stage_change date
        days_in_stage int
        probability decimal
        expected_value decimal
        status string
        source_channel string FK
    }
    
    revenue_customers {
        customer_id string PK
        account string
        segment string
        plan string
        start_date date
        mrr decimal
        new_mrr decimal
        expansion_mrr decimal
        contraction_mrr decimal
        churned_flag boolean
        churn_date date
        churn_reason string
        arpa decimal
        nrr decimal
    }
    
    benchmarks {
        channel_cpl_range string
        stage_conversion_benchmarks string
        sales_cycle_by_segment string
        nrr_targets decimal
        ltv_cac_targets decimal
        win_rate_targets decimal
        cac_payback_targets decimal
    }
    
    marketing_channels ||--o{ pipeline_deals : "generates"
    pipeline_deals ||--o{ revenue_customers : "converts_to"
    benchmarks ||--o{ marketing_channels : "targets"
    benchmarks ||--o{ pipeline_deals : "targets"
    benchmarks ||--o{ revenue_customers : "targets"
'''

write_mermaid_diagram(diagram_code, "revops_data_model")

print("\nKey Calculated Metrics:")
print("• Sales Velocity: deals_per_rep × stage_advancements_per_week")
print("• Weighted Pipeline: amount × stage_probability")
print("• CAC/LTV Ratio: LTV / CAC")
print("• Forecast MRR: weighted_pipeline - expected_churn + expansion")