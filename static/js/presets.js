/**
 * Presets and Diverse Sample Prompts for Instant Testing
 * Satisfies deliverables: "Sample outputs for at least 3 different topics"
 * and "Test with diverse topics and tones".
 */

export const SAMPLE_PRESETS = [
  {
    id: "tech_rag_blog",
    title: "🤖 Tech: AI & RAG Deep Dive",
    contentType: "blog_post",
    tone: "professional",
    length: "medium",
    topic: "Why Retrieval-Augmented Generation (RAG) is Replacing Pure LLM Fine-Tuning in 2026",
    audience: "Software Engineers & Tech Leaders",
    customInstructions: "Highlight hallucination reduction, vector embeddings, cost efficiency, and citations.",
    useRag: true,
    sampleOutput: `# Why Retrieval-Augmented Generation (RAG) is Replacing Pure LLM Fine-Tuning in 2026

## Introduction: The Enterprise AI Dilemma
In recent years, enterprises adopting artificial intelligence faced a costly question: should proprietary knowledge be baked into model weights through fine-tuning, or injected dynamically during inference?

By 2026, the consensus has tilted decisively toward **Retrieval-Augmented Generation (RAG)** [Ref 1]. While fine-tuning remains indispensable for tone calibration and specialized grammar, RAG has emerged as the architectural bedrock for real-time accuracy, data privacy, and verifiable facts.

## 1. The Cost and Freshness Advantage
Fine-tuning models on dynamic domain data resembles reprinting an encyclopedia every time a single fact changes. It is computationally expensive and introduces knowledge cutoffs.

In contrast, modern RAG decouples knowledge storage from reasoning logic:
- **Zero Retraining Cycles:** Updating an internal knowledge base takes seconds via vector re-indexing.
- **Traceable Attribution:** Every claim links directly to a verifiable chunk ID, eliminating the black-box risk.
- **Granular Access Control:** Role-based permissions can filter vector search results before prompts reach the LLM.

## 2. Grounding vs. Hallucination
Standard foundational models generate fluent yet occasionally fictional assertions. By grounding generation in validated documents [Ref 2], RAG acts as an open-book exam for the model:
1. **Semantic Chunking:** Ingesting raw PDFs and technical documents into coherent semantic passages.
2. **Dense & Lexical Hybrid Search:** Combining cosine similarity with keyword search for optimal recall.
3. **Contextual Synthesis:** Forcing strict obedience to cited passages.

## 3. Key Takeaways for Technical Leaders
- [ ] Adopt hybrid RAG architectures before allocating budget to fine-tuning.
- [ ] Invest heavily in clean document preprocessing and semantic chunking.
- [ ] Monitor token latency with local or specialized inference endpoints.

**Final Verdict:** RAG delivers the elusive trifecta of modern AI engineering: lower cost, higher accuracy, and audit-ready explainability.`
  },
  {
    id: "fitness_social",
    title: "⚡ Fitness: 15-Min Workout Hook",
    contentType: "social_caption",
    tone: "inspirational",
    length: "short",
    topic: "The 15-Minute Micro-Workout Habit for Busy High Performers",
    audience: "Busy Professionals & Entrepreneurs",
    customInstructions: "Start with a high-stakes hook, break it into 3 clear bullets, include an engaging CTA.",
    useRag: false,
    sampleOutput: `🔥 **You don't need 2 hours in the gym. You need 15 uninterrupted minutes of intensity.**

The #1 excuse holding high performers back isn't lack of discipline—it's overcomplicating fitness.

Here is the exact 15-minute micro-workout routine that will double your energy today:

⏱️ **Minute 0–5: Mobility & Nervous System Activation**
Deep bodyweight squats, cat-cow spine flows, and explosive jumping jacks.

💥 **Minute 5–12: High-Density Metabolic Circuit (45s On / 15s Off)**
1. Kettlebell Swings (posterior chain power)
2. Push-ups with tempo control (chest & core stability)
3. Reverse Lunges with reach (hip flexibility & quad load)

🧘 **Minute 12–15: Active Down-Regulation & Breathwork**
Box breathing (4s in, 4s hold, 4s out, 4s hold) to drop cortisol and prime focus.

Consistency beats intensity every single time. 15 minutes done daily beats a 2-hour workout you skip 4 days a week.

💬 *Are you ready to commit 15 minutes today? Drop a '🔥' in the comments if you're in!*

#FitnessMotivation #HighPerformance #MicroWorkouts #HealthHabits #ProductivityHacks #WorkoutRoutine`
  },
  {
    id: "business_summary",
    title: "📊 Business: Cloud Migration Briefing",
    contentType: "summary",
    tone: "academic",
    length: "short",
    topic: "Strategic Cost & Security Evaluation of Hybrid Cloud Modernization",
    audience: "C-Suite & IT Governance Boards",
    customInstructions: "Provide executive overview, quantitative risk vectors, and three phased deployment milestones.",
    useRag: true,
    sampleOutput: `# Executive Briefing: Hybrid Cloud Modernization

### 1. Executive Thesis
Legacy on-premises infrastructure presents escalating maintenance liabilities and latency bottlenecks. A staged transition to hybrid multi-cloud architecture unlocks estimated 28% total cost of ownership (TCO) reductions while establishing automated failover redundancy [Ref 3].

### 2. Core Strategic Findings
- **Operational Scalability:** Cloud-native microservices mitigate over-provisioning during peak cyclical loads.
- **Zero-Trust Security Alignment:** Implementing identity-centric access control replaces perimeter-based vulnerabilities.
- **Data Sovereignty Compliance:** Sensitive financial assets remain in dedicated on-prem enclaves while non-regulated analytics run on scalable public cloud clusters.

### 3. Phased Implementation Roadmap
1. **Phase 1 (Months 1–3): Discovery & Workload Taxonomy** — Audit existing interdependencies and container readiness.
2. **Phase 2 (Months 4–7): Core Migration & Data Pipelines** — Deploy Kubernetes orchestration and automated telemetry.
3. **Phase 3 (Months 8–12): Decommissioning & FinOps Governance** — Optimize real-time cloud spend and establish SLA governance.`
  },
  {
    id: "marketing_newsletter",
    title: "💌 Marketing: Product Launch Email",
    contentType: "email_newsletter",
    tone: "persuasive",
    length: "medium",
    topic: "Announcing NexusAI: Your Autonomous Intelligent Content Co-Pilot",
    audience: "Digital Creators & Marketing Teams",
    customInstructions: "Include 3 subject line variations, personal narrative opening, key feature breakdown, and early-bird discount code.",
    useRag: false,
    sampleOutput: `**Subject Line Options:**
• Option A: We built the AI writing assistant we always wanted 🚀
• Option B: Say goodbye to blank page syndrome forever (Meet NexusAI)
• Option C: Your new content co-pilot is finally live (+ 40% early bird)

*Preview Text: Grounded in your own documents, powered by multi-model AI, and designed for speed.*

---

Hey Creator,

How many hours did your team spend last week staring at a blinking cursor?

If you are anything like us, the hardest part of content marketing isn't having ideas—it's translating those ideas into publication-ready blog posts, captions, and executive briefs without losing your authentic brand voice.

Today, after 8 months of relentless engineering, we are proud to introduce **NexusAI Studio**.

Here is why this changes everything:

✨ **1. Grounded Knowledge (RAG):** Upload your brand PDFs, style guides, and whitepapers. NexusAI cites your facts with zero hallucinations.
✨ **2. Instant Multi-Format Publishing:** Turn one thesis into an in-depth blog post, a punchy Instagram caption, and a viral LinkedIn breakdown with one click.
✨ **3. Real-Time Analytics:** Word count, character density, and readability grades tracked live as you create.

To celebrate our launch, use code **EARLYBIRD40** at checkout this week to unlock 40% off your lifetime plan.

👉 [Claim Your Early Bird Pass Now](https://nexusai.studio/launch)

We can't wait to see what you create.

Best,
**The NexusAI Team**`
  }
];
