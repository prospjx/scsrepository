# Smart Course Scheduler (SCS) — System Architecture

![Platform Architecture](C:/Users/prosp/.gemini/antigravity-ide/brain/cfc5b0ad-9778-41c5-b378-95942f1da79a/platform_architecture_1791677085255.jpg)

---

## 1. End-to-End Cloud Platform Architecture

```mermaid
graph TD
    subgraph ClientLayer ["1. User Access Layer"]
        User["🎓 Student / Client Web Browser"]
    end

    subgraph EdgeLayer ["2. Global CDN & Edge (AWS)"]
        CF["🌐 Amazon CloudFront CDN<br/>(d3vd2js7hc9dyq.cloudfront.net)"]
        S3["📦 Amazon S3 Bucket<br/>(Static SPA Assets, HTML, CSS, JS)"]
    end

    subgraph IngressLayer ["3. Ingress & Load Balancing"]
        ELB["⚖️ AWS Classic ELB<br/>(Mapped to CloudFront /api/*)"]
    end

    subgraph EKS ["4. Amazon EKS Cluster (Kubernetes v1.31)"]
        direction TB

        subgraph Gateway ["API Gateway & Orchestrator"]
            SCH["⚡ schedulerapi (Port 8000)<br/>• Reverse Proxy (/api/v1/*)<br/>• Backtracking CSP Scheduler"]
        end

        subgraph CoreServices ["Application Microservices"]
            CRS["📚 courseapi (ClusterIP :8001)<br/>• Catalog & Section Management"]
            STU["👤 studentapi (ClusterIP :8002)<br/>• Profiles, Transcripts & Routine Prefs"]
            AI["🤖 ai-assistant-api (ClusterIP :8003)<br/>• Multimodal Vision & 7-Day Life Planner"]
        end

        subgraph DataLayer ["Stateful Persistence"]
            PG[("🐘 PostgreSQL 16<br/>courses_db | students_db | scheduler_db")]
        end

        subgraph Observability ["Observability & GitOps"]
            ARGO["🐙 ArgoCD (App-of-Apps)<br/>Continuous Delivery Controller"]
            PROM["🔥 Prometheus Server (:9090)<br/>Scrapes /metrics on microservices"]
            GRAF["📊 Grafana (:3000)<br/>Pre-built KPI Dashboards"]
            LOKI["🪵 Loki & Promtail<br/>Log Aggregation Engine"]
        end
    end

    subgraph ExternalServices ["5. External AI Cloud"]
        GEMINI["✨ Google Gemini API<br/>(gemini-2.5-flash Multimodal Model)"]
    end

    %% Client and Edge connections
    User -->|HTTPS| CF
    CF -->|"Static Files (/*)"| S3
    CF -->|"API Calls (/api/*)<br/>(60s timeout)"| ELB
    ELB -->|Port 8000| SCH

    %% Internal Routing
    SCH -->|"Proxy /courses/* (:8001)"| CRS
    SCH -->|"Proxy /students/* (:8002)"| STU
    SCH -->|"Proxy /analyze/* (:8003)"| AI

    %% Database connections
    CRS -->|"TCP 5432"| PG
    STU -->|"TCP 5432"| PG
    SCH -->|"TCP 5432"| PG

    %% AI Integration
    AI -->|"HTTPS REST (Image & JSON Prompt)"| GEMINI

    %% GitOps & Monitoring
    PROM -.->|"Scrape /metrics"| SCH
    PROM -.->|"Scrape /metrics"| CRS
    PROM -.->|"Scrape /metrics"| STU
    PROM -.->|"Scrape /metrics"| AI
    GRAF -.->|"Query PromQL & Loki"| PROM
