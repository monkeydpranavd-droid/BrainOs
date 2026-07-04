export interface SystemSettings {
  model: string;
  syncSpeed: string;
  vectorLimit: string;
  apiToken: string;
}

export async function getSettings(): Promise<SystemSettings> {
  return {
    model: 'gemini-2.5-pro',
    syncSpeed: 'realtime',
    vectorLimit: '10000',
    apiToken: 'brain_live_382103fca9188a9c80d2'
  };
}

export async function saveSettings(settings: SystemSettings): Promise<boolean> {
  await new Promise(resolve => setTimeout(resolve, 600));
  return true;
}
