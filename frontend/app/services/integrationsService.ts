import { Slack, Github, HardDrive } from 'lucide-react';

export interface IntegrationItem {
  id: string;
  name: string;
  desc: string;
  status: 'active' | 'syncing' | 'error';
  stats: {
    volume: string;
    activity: string;
    interval: string;
  };
}

export async function getIntegrations(): Promise<IntegrationItem[]> {
  return [
    {
      id: 'slack',
      name: 'Slack Workspace Sync',
      desc: 'Realtime chat event-listener tracking engineering channels, user presence, and team threads.',
      status: 'active',
      stats: { volume: '148 channels', activity: '12.4k/day', interval: 'Real-time' }
    },
    {
      id: 'github',
      name: 'GitHub Repository Hook',
      desc: 'Automatically synchronizes repositories, code README structures, Pull Request logs, and inline comments.',
      status: 'active',
      stats: { volume: '32 repos', activity: '1.2k commits/wk', interval: 'Instant webhook' }
    },
    {
      id: 'drive',
      name: 'Google Drive indexer',
      desc: 'Scheduled indexing agent walking document hierarchies, schemas, and presentation materials.',
      status: 'syncing',
      stats: { volume: '4.2k files', activity: '150 files/hr', interval: 'Syncing (88%)' }
    }
  ];
}
