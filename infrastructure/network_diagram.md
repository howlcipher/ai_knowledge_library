# Architecture Diagrams

This document maps out the standard personal homelab architecture as well as primary Cloud Architectures (AWS/GCP).

## Homelab Architecture

```mermaid
graph TD;
    WAN(Internet) --> EdgeRouter(Meraki MX Firewall);
    EdgeRouter --> CoreSwitch(Cisco Catalyst Switch);
    CoreSwitch --> Server1(Proxmox Hypervisor 1);
    CoreSwitch --> Server2(Proxmox Hypervisor 2);
    Server1 --> VM1(Docker Swarm Manager);
    Server1 --> VM2(GitLab Server);
    Server2 --> VM3(Docker Swarm Worker);
    Server2 --> VM4(Database Server);
```

## AWS Cloud Architecture

```mermaid
graph TD;
    Internet --> ALB(Application Load Balancer);
    ALB --> EKS_Cluster(EKS Kubernetes Cluster);
    EKS_Cluster --> RDS(RDS Postgres Database);
    EKS_Cluster --> ElastiCache(Redis Cache);
    EKS_Cluster --> S3(S3 Object Storage);
```

## GCP Cloud Architecture

```mermaid
graph TD;
    Internet --> CloudLoadBalancer(Cloud Load Balancer);
    CloudLoadBalancer --> GKE_Cluster(GKE Kubernetes Cluster);
    GKE_Cluster --> CloudSQL(Cloud SQL Database);
    GKE_Cluster --> CloudStorage(Cloud Storage Bucket);
    GKE_Cluster --> PubSub(Pub/Sub Message Broker);
```
