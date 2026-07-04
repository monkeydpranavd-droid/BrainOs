import { entities } from '../mockData';

export interface DashboardStats {
  documentsIndexed: string;
  knowledgeNodes: string;
  aiQueriesToday: string;
  connectedIntegrations: string;
}

export interface SyncLog {
  time: string;
  type: string;
  action: string;
}

export interface DensityItem {
  name: string;
  nodes: number;
}

export async function getDashboardStats(): Promise<DashboardStats> {
  // Simulating async API call behavior
  return {
    documentsIndexed: "347 Docs",
    knowledgeNodes: "18,492 Nodes",
    aiQueriesToday: "1,240",
    connectedIntegrations: "3 Active"
  };
}

export async function getRecentSyncActions(): Promise<SyncLog[]> {
  return [
    { time: 'Just now', type: 'Google Drive', action: 'Indexed doc: Payments API Integration Roadmap' },
    { time: '3m ago', type: 'Slack Sync', action: 'Parsed 14 relational links in #auth-protocols' },
    { time: '12m ago', type: 'GitHub Hook', action: 'Scanned commits inside brainos-org/atlas-search' },
    { time: '1h ago', type: 'Notion Sync', action: 'Synchronized company onboarding specs' }
  ];
}

export async function getNodeDensity(): Promise<DensityItem[]> {
  return [
    { name: 'People', nodes: entities.filter(e => e.type === 'person').length },
    { name: 'Projects', nodes: entities.filter(e => e.type === 'project').length },
    { name: 'Docs', nodes: entities.filter(e => e.type === 'document').length },
    { name: 'Tech', nodes: entities.filter(e => e.type === 'technology').length },
    { name: 'Meetings', nodes: entities.filter(e => e.type === 'meeting').length },
    { name: 'Depts', nodes: entities.filter(e => e.type === 'department').length },
    { name: 'Connectors', nodes: entities.filter(e => e.type === 'integration').length },
  ];
}
