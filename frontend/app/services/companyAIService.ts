export interface AIResponse {
  text: string;
  citations: string[];
}

export async function sendMessageToAI(text: string): Promise<AIResponse> {
  // Mimic network latency
  await new Promise(resolve => setTimeout(resolve, 800));

  const queryLower = text.toLowerCase();
  let responseText = "I found matching relational information in our company brain.";
  let citations: string[] = [];

  if (queryLower.includes('payments') || queryLower.includes('jane')) {
    responseText = "Jane Doe is the Lead Architect and Lead Engineer of Payments 2.0. She works in the Core Engineering Division. The Payments 2.0 project uses TypeScript and Rust/FFI hooks, and references the Payments API Integration Roadmap documentation.";
    citations = ['person-jane', 'project-payments', 'doc-payments-api', 'tech-typescript', 'tech-rust'];
  } else if (queryLower.includes('atlas') || queryLower.includes('search')) {
    responseText = "Project Atlas is a next-generation semantic search mapping system built with Next.js 15 and TypeScript. Alex Rivera is the Principal Product Manager, and Jane Doe acts as an Advisor. Key progress is tracked in the Atlas Bi-Weekly Architecture Sync meetings.";
    citations = ['project-atlas', 'person-alex', 'person-jane', 'tech-nextjs', 'tech-typescript', 'meeting-sync'];
  } else if (queryLower.includes('onboarding') || queryLower.includes('guide')) {
    responseText = "The Company Onboarding Playbook is stored in Notion and was authored by Principal PM Alex Rivera. It serves as a guide for the Core Engineering Division, detailing local developer tools and guidelines.";
    citations = ['doc-onboarding', 'person-alex', 'dept-engineering'];
  } else if (queryLower.includes('auth') || queryLower.includes('security')) {
    responseText = "Sarah Chen (Senior Security Specialist) authored the Enterprise Authentication Specs stored in Google Drive. This document secures the checkout and billing flows of Payments 2.0, utilizing OAuth2 and SAML.";
    citations = ['doc-auth', 'person-sarah', 'project-payments'];
  } else {
    responseText = "I searched our synced repositories. I found references to Jane Doe (Engineering), Alex Rivera (Product), Sarah Chen (Security), and systems like Project Atlas and Payments 2.0. Let me know if you would like me to summarize any of these nodes.";
    citations = ['person-jane', 'person-alex', 'person-sarah', 'project-atlas', 'project-payments'];
  }

  return {
    text: responseText,
    citations
  };
}
