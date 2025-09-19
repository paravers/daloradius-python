# daloradius-python Python版本项目架构设计（Mermaid UML）

## 执行概述
基于当前架构评审结果和重构目标，设计现代化的Python版本项目架构，采用微服务、前后端分离和云原生设计模式，解决现有技术债务并提升系统整体能力。

## 技术栈选型

### 后端框架
- **主框架**：FastAPI（高性能异步框架）
- **ORM**：SQLAlchemy 2.0（现代化ORM）
- **数据库**：PostgreSQL（主数据库） + Redis（缓存）
- **消息队列**：RabbitMQ或Apache Kafka
- **任务调度**：Celery

### 前端技术
- **主框架**：Vue.js 3 + TypeScript
- **UI组件库**：Element Plus
- **状态管理**：Pinia
- **构建工具**：Vite

### 基础设施
- **容器化**：Docker + Kubernetes
- **API网关**：Kong或Nginx
- **监控**：Prometheus + Grafana
- **日志**：ELK Stack

## 系统架构设计

```mermaid
graph TB
    subgraph "Client Layer"
        WebApp[Vue.js Web App]
        MobileApp[Mobile App]
        ThirdParty[Third Party Integrations]
    end
    
    subgraph "Edge Layer"
        LB[Load Balancer]
        CDN[CDN]
        WAF[Web Application Firewall]
    end
    
    subgraph "API Gateway Layer"
        Gateway[Kong API Gateway]
        Auth[Auth Service]
        RateLimit[Rate Limiting]
    end
    
    subgraph "Application Services"
        subgraph "Core Services"
            UserSvc[User Service]
            AcctSvc[Accounting Service]
            BillSvc[Billing Service]
            ReportSvc[Report Service]
            ConfigSvc[Configuration Service]
        end
        
        subgraph "Support Services"
            NotifSvc[Notification Service]
            FileSvc[File Service]
            AuditSvc[Audit Service]
            IntegSvc[Integration Service]
        end
    end
    
    subgraph "Data Layer"
        subgraph "Databases"
            MainDB[(PostgreSQL)]
            RadiusDB[(RADIUS DB)]
            AnalyticsDB[(ClickHouse)]
        end
        
        subgraph "Cache & Queue"
            Redis[(Redis Cache)]
            MessageQ[Message Queue]
        end
        
        subgraph "Storage"
            FileStore[File Storage]
            LogStore[Log Storage]
        end
    end
    
    subgraph "Infrastructure"
        Monitor[Monitoring]
        Logging[Centralized Logging]
        Backup[Backup Service]
    end
    
    WebApp --> LB
    MobileApp --> LB
    ThirdParty --> Gateway
    
    LB --> WAF
    CDN --> WAF
    WAF --> Gateway
    
    Gateway --> Auth
    Gateway --> RateLimit
    Gateway --> UserSvc
    Gateway --> AcctSvc
    Gateway --> BillSvc
    Gateway --> ReportSvc
    Gateway --> ConfigSvc
    
    UserSvc --> NotifSvc
    BillSvc --> NotifSvc
    AcctSvc --> AuditSvc
    BillSvc --> AuditSvc
    
    UserSvc --> MainDB
    AcctSvc --> RadiusDB
    BillSvc --> MainDB
    ReportSvc --> AnalyticsDB
    ConfigSvc --> MainDB
    
    UserSvc --> Redis
    AcctSvc --> Redis
    BillSvc --> Redis
    
    NotifSvc --> MessageQ
    FileSvc --> FileStore
    AuditSvc --> LogStore
    
    Monitor --> UserSvc
    Monitor --> AcctSvc
    Monitor --> BillSvc
    Logging --> UserSvc
    Logging --> AcctSvc
    Logging --> BillSvc
```

## 微服务架构设计

```mermaid
graph LR
    subgraph "User Domain"
        UserAPI[User API]
        UserDB[(User Database)]
        UserCache[(User Cache)]
    end
    
    subgraph "Accounting Domain"
        AcctAPI[Accounting API]
        AcctDB[(RADIUS Database)]
        AcctCache[(Acct Cache)]
        AcctWorker[Background Workers]
    end
    
    subgraph "Billing Domain"
        BillAPI[Billing API]
        BillDB[(Billing Database)]
        BillCache[(Bill Cache)]
        BillWorker[Billing Workers]
    end
    
    subgraph "Reporting Domain"
        ReportAPI[Report API]
        ReportDB[(Analytics DB)]
        ReportCache[(Report Cache)]
        ReportWorker[Report Workers]
    end
    
    subgraph "Shared Services"
        AuthSvc[Authentication]
        NotifSvc[Notification]
        FileSvc[File Service]
        ConfigSvc[Configuration]
    end
    
    UserAPI --> UserDB
    UserAPI --> UserCache
    UserAPI --> AuthSvc
    
    AcctAPI --> AcctDB
    AcctAPI --> AcctCache
    AcctAPI --> AcctWorker
    AcctAPI --> AuthSvc
    
    BillAPI --> BillDB
    BillAPI --> BillCache
    BillAPI --> BillWorker
    BillAPI --> NotifSvc
    BillAPI --> AuthSvc
    
    ReportAPI --> ReportDB
    ReportAPI --> ReportCache
    ReportAPI --> ReportWorker
    ReportAPI --> AuthSvc
    
    AuthSvc --> UserDB
    NotifSvc --> FileSvc
    ConfigSvc --> UserDB
```

## 数据架构设计

```mermaid
erDiagram
    USERS ||--o{ USER_SESSIONS : has
    USERS ||--o{ USER_PROFILES : has
    USERS ||--o{ ACCOUNTING_RECORDS : generates
    USERS ||--o{ BILLING_RECORDS : has
    
    USER_PROFILES ||--o{ BILLING_PLANS : subscribes
    BILLING_PLANS ||--o{ BILLING_RATES : contains
    
    ACCOUNTING_RECORDS ||--o{ BILLING_RECORDS : generates
    BILLING_RECORDS ||--o{ INVOICES : included_in
    INVOICES ||--o{ PAYMENTS : paid_by
    
    OPERATORS ||--o{ AUDIT_LOGS : creates
    OPERATORS ||--o{ CONFIGURATIONS : manages
    
    USERS {
        uuid id PK
        string username UK
        string email UK
        string password_hash
        timestamp created_at
        timestamp updated_at
        boolean is_active
    }
    
    USER_PROFILES {
        uuid id PK
        uuid user_id FK
        string first_name
        string last_name
        string phone
        json attributes
        timestamp created_at
        timestamp updated_at
    }
    
    ACCOUNTING_RECORDS {
        uuid id PK
        uuid user_id FK
        string session_id
        timestamp start_time
        timestamp stop_time
        bigint bytes_in
        bigint bytes_out
        string nas_ip
        timestamp created_at
    }
    
    BILLING_RECORDS {
        uuid id PK
        uuid user_id FK
        uuid accounting_id FK
        decimal amount
        string currency
        timestamp billing_date
        string status
        timestamp created_at
    }
    
    INVOICES {
        uuid id PK
        uuid user_id FK
        string invoice_number UK
        decimal total_amount
        string currency
        timestamp due_date
        string status
        timestamp created_at
    }
```

## 安全架构设计

```mermaid
graph TB
    subgraph "Security Layers"
        subgraph "Edge Security"
            WAF[Web Application Firewall]
            DDoS[DDoS Protection]
            SSL[SSL/TLS Termination]
        end
        
        subgraph "Authentication & Authorization"
            OAuth[OAuth 2.0 / OIDC]
            JWT[JWT Tokens]
            RBAC[Role-Based Access Control]
            MFA[Multi-Factor Authentication]
        end
        
        subgraph "Application Security"
            InputVal[Input Validation]
            CSRF[CSRF Protection]
            XSS[XSS Protection]
            SQLInj[SQL Injection Prevention]
        end
        
        subgraph "Data Security"
            Encrypt[Data Encryption]
            Backup[Secure Backup]
            Audit[Security Audit]
            PII[PII Protection]
        end
        
        subgraph "Infrastructure Security"
            NetworkSeg[Network Segmentation]
            Firewall[Internal Firewalls]
            SecretMgmt[Secret Management]
            ContainerSec[Container Security]
        end
    end
    
    WAF --> OAuth
    DDoS --> OAuth
    SSL --> OAuth
    
    OAuth --> InputVal
    JWT --> InputVal
    RBAC --> InputVal
    MFA --> InputVal
    
    InputVal --> Encrypt
    CSRF --> Encrypt
    XSS --> Encrypt
    SQLInj --> Encrypt
    
    Encrypt --> NetworkSeg
    Backup --> NetworkSeg
    Audit --> NetworkSeg
    PII --> NetworkSeg
```

## 部署架构设计

```mermaid
graph TB
    subgraph "Production Environment"
        subgraph "Kubernetes Cluster"
            subgraph "Frontend"
                FE1[Web App Pod 1]
                FE2[Web App Pod 2]
                FEN[Web App Pod N]
            end
            
            subgraph "API Gateway"
                GW1[Gateway Pod 1]
                GW2[Gateway Pod 2]
            end
            
            subgraph "Microservices"
                US1[User Service Pod]
                AS1[Acct Service Pod]
                BS1[Bill Service Pod]
                RS1[Report Service Pod]
            end
            
            subgraph "Shared Services"
                AUTH[Auth Service]
                NOTIF[Notification Service]
                FILE[File Service]
            end
        end
        
        subgraph "Data Tier"
            PG[(PostgreSQL Cluster)]
            REDIS[(Redis Cluster)]
            MQ[Message Queue Cluster]
        end
        
        subgraph "Storage"
            NFS[Network File System]
            S3[Object Storage]
        end
        
        subgraph "Monitoring"
            PROM[Prometheus]
            GRAF[Grafana]
            ELK[ELK Stack]
        end
    end
    
    subgraph "External Services"
        LB[Load Balancer]
        DNS[DNS Service]
        CDN[CDN Service]
    end
    
    DNS --> LB
    LB --> GW1
    LB --> GW2
    CDN --> FE1
    CDN --> FE2
    
    GW1 --> US1
    GW1 --> AS1
    GW1 --> BS1
    GW1 --> RS1
    
    US1 --> PG
    AS1 --> PG
    BS1 --> PG
    RS1 --> PG
    
    US1 --> REDIS
    AS1 --> REDIS
    BS1 --> REDIS
    
    NOTIF --> MQ
    FILE --> NFS
    FILE --> S3
    
    PROM --> US1
    PROM --> AS1
    PROM --> BS1
    GRAF --> PROM
    ELK --> US1
    ELK --> AS1
    ELK --> BS1
```

## 架构特性说明

### 高可用性设计
- **服务冗余**：每个服务多实例部署
- **数据库集群**：主从复制 + 读写分离
- **负载均衡**：多层负载均衡策略
- **故障转移**：自动故障检测和切换

### 可扩展性设计
- **水平扩展**：服务无状态化，支持水平扩展
- **微服务架构**：按业务域拆分，独立扩展
- **缓存策略**：多级缓存提升性能
- **异步处理**：消息队列处理长时间任务

### 安全性设计
- **零信任架构**：服务间通信加密验证
- **最小权限原则**：精细化权限控制
- **数据保护**：加密存储和传输
- **安全监控**：全链路安全审计

### 可观测性设计
- **指标监控**：业务和技术指标监控
- **日志聚合**：结构化日志集中管理
- **链路追踪**：分布式请求追踪
- **告警机制**：智能告警和通知

---

本Python架构设计为daloradius重构提供现代化、可扩展的技术方案。