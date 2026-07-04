export interface AnalyticsStats {
  speed: string;
  cacheHit: string;
  accuracy: string;
}

export interface IngestionData {
  name: string;
  documents: number;
  messages: number;
}

export interface SourceData {
  name: string;
  value: number;
  color: string;
}

export interface QueryPerf {
  day: string;
  speed: number;
}

export async function getAnalyticsStats(): Promise<AnalyticsStats> {
  return {
    speed: "41.8 files/m",
    cacheHit: "96.4%",
    accuracy: "99.82%"
  };
}

export async function getIngestionStream(): Promise<IngestionData[]> {
  return [
    { name: '08:00', documents: 24, messages: 120 },
    { name: '10:00', documents: 86, messages: 340 },
    { name: '12:00', documents: 45, messages: 210 },
    { name: '14:00', documents: 110, messages: 450 },
    { name: '16:00', documents: 95, messages: 390 },
    { name: '18:00', documents: 30, messages: 180 },
  ];
}

export async function getSourceDistribution(): Promise<SourceData[]> {
  return [
    { name: 'Slack Sync', value: 48, color: '#6366f1' },
    { name: 'Google Drive', value: 25, color: '#38bdf8' },
    { name: 'GitHub Hook', value: 17, color: '#34d399' },
    { name: 'Other (Confluence)', value: 10, color: '#a78bfa' },
  ];
}

export async function getQueryPerformance(): Promise<QueryPerf[]> {
  return [
    { day: 'Mon', speed: 14 },
    { day: 'Tue', speed: 16 },
    { day: 'Wed', speed: 20 },
    { day: 'Thu', speed: 18 },
    { day: 'Fri', speed: 15 },
    { day: 'Sat', speed: 11 },
    { day: 'Sun', speed: 12 },
  ];
}
