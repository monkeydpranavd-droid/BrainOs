export interface Entity {
  id: string;
  name: string;
  type: 'person' | 'project' | 'document' | 'technology' | 'meeting' | 'department' | 'integration';
  details: string;
  meta: Record<string, string | string[]>;
}

export interface Relationship {
  source: string;
  target: string;
  type: string;
}

export const entities: Entity[] = [
  // People
  {
    id: "person-jane",
    name: "Jane Doe",
    type: "person",
    details: "Lead Architect of BrainOS Core and Payments 2.0. Has 8+ years of distributed system design experience.",
    meta: {
      role: "Staff Software Engineer",
      department: "Engineering",
      slackStatus: "active",
      email: "jane.doe@brainos.ai"
    }
  },
  {
    id: "person-alex",
    name: "Alex Rivera",
    type: "person",
    details: "Senior Product Manager specializing in AI search capabilities and collaboration workspaces. Designing Atlas.",
    meta: {
      role: "Principal Product Manager",
      department: "Product",
      slackStatus: "in-meetings",
      email: "alex.rivera@brainos.ai"
    }
  },
  {
    id: "person-sarah",
    name: "Sarah Chen",
    type: "person",
    details: "Senior Security Engineer auditing authentication protocols and database access controls.",
    meta: {
      role: "Senior Security Specialist",
      department: "Security",
      slackStatus: "away",
      email: "sarah.chen@brainos.ai"
    }
  },

  // Projects
  {
    id: "project-atlas",
    name: "Project Atlas",
    type: "project",
    details: "The next-generation semantic search mapping system built to synchronize cloud enterprise file repositories.",
    meta: {
      status: "In Progress",
      timeline: "Q3 - Q4 2026",
      repository: "github.com/brainos-org/atlas-search"
    }
  },
  {
    id: "project-payments",
    name: "Payments 2.0",
    type: "project",
    details: "Overhaul of the core checkout and billing engine to support multi-currency, direct banking FFI integrations.",
    meta: {
      status: "Beta Testing",
      timeline: "Q2 - Q3 2026",
      repository: "github.com/brainos-org/checkout-payments"
    }
  },

  // Documents
  {
    id: "doc-auth",
    name: "Enterprise Authentication Specs",
    type: "document",
    details: "Detailed specification of OAuth2, JWT mechanisms, SAML, and Single Sign-On configs for BrainOS customers.",
    meta: {
      source: "Google Drive",
      lastUpdated: "2026-06-15",
      author: "Sarah Chen"
    }
  },
  {
    id: "doc-onboarding",
    name: "Company Onboarding Playbook",
    type: "document",
    details: "Guide on engineering setup, environment keys, local dev tools, and slack community guidelines.",
    meta: {
      source: "Notion",
      lastUpdated: "2026-05-20",
      author: "Alex Rivera"
    }
  },
  {
    id: "doc-payments-api",
    name: "Payments API Integration Roadmap",
    type: "document",
    details: "Detailed endpoints for refund routing, transaction states, webhooks, and secure FFI bridges.",
    meta: {
      source: "Confluence",
      lastUpdated: "2026-07-01",
      author: "Jane Doe"
    }
  },

  // Technologies
  {
    id: "tech-nextjs",
    name: "Next.js 15",
    type: "technology",
    details: "React Framework for production, utilized for the command bar search interface and page routing layouts.",
    meta: {
      version: "15.0.0",
      category: "Frontend Framework"
    }
  },
  {
    id: "tech-typescript",
    name: "TypeScript",
    type: "technology",
    details: "Type-safe superset of JavaScript representing our entire platform coding standards.",
    meta: {
      version: "5.4",
      category: "Programming Language"
    }
  },
  {
    id: "tech-rust",
    name: "Rust / FFI Hooks",
    type: "technology",
    details: "High-performance processing engines used for indexing multi-format raw files.",
    meta: {
      version: "1.78",
      category: "Systems Language"
    }
  },

  // Meetings
  {
    id: "meeting-sync",
    name: "Atlas Bi-Weekly Architecture Sync",
    type: "meeting",
    details: "Engineering discussion on mapping semantic chunk connections and indexing Slack history.",
    meta: {
      date: "2026-07-02",
      attendees: ["Jane Doe", "Alex Rivera"],
      recording: "drive.google.com/meet/atlas-sync-0702"
    }
  },

  // Departments
  {
    id: "dept-engineering",
    name: "Core Engineering Division",
    type: "department",
    details: "Team in charge of core microservices, system reliability, security architectures, and UI platforms.",
    meta: {
      membersCount: "42",
      lead: "Jane Doe"
    }
  },

  // Integrations
  {
    id: "integ-slack",
    name: "Slack Sync Integration",
    type: "integration",
    details: "Realtime listener indexing channels, chat messages, threads, and files.",
    meta: {
      status: "Connected",
      syncedChannels: "148"
    }
  },
  {
    id: "integ-github",
    name: "GitHub Repository Hook",
    type: "integration",
    details: "Syncs code structure, README files, commit messages, and PR review conversations.",
    meta: {
      status: "Connected",
      syncedRepos: "32"
    }
  },
  {
    id: "integ-drive",
    name: "Google Drive indexer",
    type: "integration",
    details: "Indexes DOCX, spreadsheets, slide presentations, and shared architecture maps.",
    meta: {
      status: "Syncing (88%)",
      filesIndexed: "4,210"
    }
  }
];

export const relationships: Relationship[] = [
  // Jane relations
  { source: "person-jane", target: "project-payments", type: "Lead Engineer" },
  { source: "person-jane", target: "project-atlas", type: "Advisor" },
  { source: "person-jane", target: "dept-engineering", type: "Manager / Lead" },
  { source: "person-jane", target: "doc-payments-api", type: "Author" },
  { source: "person-jane", target: "meeting-sync", type: "Speaker" },
  { source: "person-jane", target: "tech-rust", type: "Specialist" },

  // Alex relations
  { source: "person-alex", target: "project-atlas", type: "Product Manager" },
  { source: "person-alex", target: "doc-onboarding", type: "Author" },
  { source: "person-alex", target: "meeting-sync", type: "Facilitator" },

  // Sarah relations
  { source: "person-sarah", target: "doc-auth", type: "Author" },
  { source: "person-sarah", target: "project-payments", type: "Security Lead" },

  // Project Atlas relations
  { source: "project-atlas", target: "tech-nextjs", type: "Built with" },
  { source: "project-atlas", target: "tech-typescript", type: "Uses" },
  { source: "project-atlas", target: "meeting-sync", type: "Tracks progress in" },
  { source: "project-atlas", target: "integ-github", type: "Code source" },

  // Payments 2.0 relations
  { source: "project-payments", target: "tech-typescript", type: "Uses" },
  { source: "project-payments", target: "tech-rust", type: "Uses" },
  { source: "project-payments", target: "doc-payments-api", type: "Reference" },
  { source: "project-payments", target: "integ-drive", type: "Doc sync source" },

  // Document relations
  { source: "doc-auth", target: "project-payments", type: "Secures" },
  { source: "doc-onboarding", target: "dept-engineering", type: "Guide for" },

  // Integration relations
  { source: "integ-slack", target: "meeting-sync", type: "Ingests chats about" },
  { source: "integ-github", target: "tech-typescript", type: "Tracks code" }
];

export function getConnectedEntities(id: string): { entity: Entity; type: string }[] {
  const connected: { entity: Entity; type: string }[] = [];
  
  for (const rel of relationships) {
    if (rel.source === id) {
      const match = entities.find(e => e.id === rel.target);
      if (match) connected.push({ entity: match, type: rel.type });
    } else if (rel.target === id) {
      const match = entities.find(e => e.id === rel.source);
      if (match) connected.push({ entity: match, type: rel.type });
    }
  }
  
  return connected;
}

export function searchBrain(query: string): Entity[] {
  const cleanQuery = query.toLowerCase().trim();
  if (!cleanQuery) return [];
  
  return entities.filter(e => 
    e.name.toLowerCase().includes(cleanQuery) || 
    e.details.toLowerCase().includes(cleanQuery) ||
    e.type.toLowerCase().includes(cleanQuery) ||
    (typeof e.meta.role === 'string' && e.meta.role.toLowerCase().includes(cleanQuery)) ||
    (typeof e.meta.author === 'string' && e.meta.author.toLowerCase().includes(cleanQuery))
  );
}
