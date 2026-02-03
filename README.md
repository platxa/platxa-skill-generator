# Claude Code Skills Registry

> A curated, quality-verified collection of production-ready skills for Claude Code CLI.
>
> **Maintained by**: [Platxa](https://platxa.com) | **License**: MIT | **Compatible with**: `npx skills`

**100 skills** across **16 categories** — 21 local, 79 external

---

## Quick Install

```bash
# Clone the repository
git clone https://github.com/platxa/platxa-skill-generator.git
cd platxa-skill-generator

# Install a single skill
./scripts/install-from-catalog.sh <skill-name>

# Install to project instead of user directory
./scripts/install-from-catalog.sh <skill-name> --project

# Install all essential skills (tier 1)
./scripts/install-from-catalog.sh --all --tier 1

# List all available skills
./scripts/install-from-catalog.sh --list
```

---

## Skills Index

| Skill | Trust | Description | Category | Tier | Tokens | Source | Install |
|-------|-------|-------------|----------|------|--------|--------|---------|
| [platxa-error-handling](skills/platxa-error-handling/SKILL.md) | ![trust](badges/platxa-error-handling.svg) | Guide for structured error handling across Platxa stack. Covers error types, ... | backend | Internal | 7,013 | Platxa | `./scripts/install-from-catalog.sh platxa-error-handling` |
| [platxa-sidecar-builder](skills/platxa-sidecar-builder/SKILL.md) | ![trust](badges/platxa-sidecar-builder.svg) | Build Node.js sidecar services for real-time code editing platforms. Covers f... | backend | Internal | 7,475 | Platxa | `./scripts/install-from-catalog.sh platxa-sidecar-builder` |
| [platxa-yjs-server](skills/platxa-yjs-server/SKILL.md) | ![trust](badges/platxa-yjs-server.svg) | Yjs WebSocket server implementation guide for real-time collaboration. Config... | backend | Internal | 5,407 | Platxa | `./scripts/install-from-catalog.sh platxa-yjs-server` |
| [code-documenter](skills/code-documenter/SKILL.md) | ![trust](badges/code-documenter.svg) | Automatically generates and improves code documentation across Python, JavaSc... | devtools | Internal | 3,605 | Platxa | `./scripts/install-from-catalog.sh code-documenter` |
| [platxa-frontend-builder](skills/platxa-frontend-builder/SKILL.md) | ![trust](badges/platxa-frontend-builder.svg) | Generate production-ready React/Next.js components for Platxa platform. Creat... | frontend | Internal | 7,468 | Platxa | `./scripts/install-from-catalog.sh platxa-frontend-builder` |
| [platxa-monaco-config](skills/platxa-monaco-config/SKILL.md) | ![trust](badges/platxa-monaco-config.svg) | Monaco editor configuration guide for Platxa platform. Configure themes, keyb... | frontend | Internal | 5,873 | Platxa | `./scripts/install-from-catalog.sh platxa-monaco-config` |
| [platxa-preview-service](skills/platxa-preview-service/SKILL.md) | ![trust](badges/platxa-preview-service.svg) | Live preview service for Odoo themes with real-time token updates, SCSS compi... | frontend | Internal | 1,764 | Platxa | `./scripts/install-from-catalog.sh platxa-preview-service` |
| [platxa-token-sync](skills/platxa-token-sync/SKILL.md) | ![trust](badges/platxa-token-sync.svg) | Transform Brand Kit design tokens (OKLCH colors, spacing, typography) into Od... | frontend | Internal | 6,793 | Platxa | `./scripts/install-from-catalog.sh platxa-token-sync` |
| [commit-message](skills/commit-message/SKILL.md) | ![trust](badges/commit-message.svg) | Generate conventional commit messages by analyzing staged git changes. Detect... | git | Internal | 2,475 | Platxa | `./scripts/install-from-catalog.sh commit-message` |
| [pr-description](skills/pr-description/SKILL.md) | ![trust](badges/pr-description.svg) | Generate comprehensive pull request descriptions by analyzing git commits and... | git | Internal | 2,467 | Platxa | `./scripts/install-from-catalog.sh pr-description` |
| [platxa-k8s-ops](skills/platxa-k8s-ops/SKILL.md) | ![trust](badges/platxa-k8s-ops.svg) | Kubernetes operations automation for Platxa platform. Debug instances, manage... | infrastructure | Internal | 6,064 | Platxa | `./scripts/install-from-catalog.sh platxa-k8s-ops` |
| [platxa-k8s-scaling](skills/platxa-k8s-scaling/SKILL.md) | ![trust](badges/platxa-k8s-scaling.svg) | Kubernetes scaling patterns for Platxa platform. Configure scale-to-zero with... | infrastructure | Internal | 5,551 | Platxa | `./scripts/install-from-catalog.sh platxa-k8s-scaling` |
| [platxa-logging](skills/platxa-logging/SKILL.md) | ![trust](badges/platxa-logging.svg) | Structured logging and correlation ID patterns for Platxa services. Covers Py... | observability | Internal | 6,683 | Platxa | `./scripts/install-from-catalog.sh platxa-logging` |
| [platxa-monitoring](skills/platxa-monitoring/SKILL.md) | ![trust](badges/platxa-monitoring.svg) | Observability guide for Platxa platform using Prometheus metrics and Loki log... | observability | Internal | 6,739 | Platxa | `./scripts/install-from-catalog.sh platxa-monitoring` |
| [platxa-odoo-blog](skills/platxa-odoo-blog/SKILL.md) | ![trust](badges/platxa-odoo-blog.svg) | Generate Odoo blog templates with post layouts, category pages, author profil... | odoo | Internal | 2,953 | Platxa | `./scripts/install-from-catalog.sh platxa-odoo-blog` |
| [platxa-odoo-form](skills/platxa-odoo-form/SKILL.md) | ![trust](badges/platxa-odoo-form.svg) | Generate Odoo website forms with CRM lead integration, field validation, cond... | odoo | Internal | 4,342 | Platxa | `./scripts/install-from-catalog.sh platxa-odoo-form` |
| [platxa-odoo-page](skills/platxa-odoo-page/SKILL.md) | ![trust](badges/platxa-odoo-page.svg) | Generate complete Odoo website pages (About, Contact, Services, Team, FAQ, Pr... | odoo | Internal | 6,834 | Platxa | `./scripts/install-from-catalog.sh platxa-odoo-page` |
| [platxa-jwt-auth](skills/platxa-jwt-auth/SKILL.md) | ![trust](badges/platxa-jwt-auth.svg) | Generate RS256 JWT authentication with JWKS endpoint for Platxa services. Cre... | security | Internal | 6,318 | Platxa | `./scripts/install-from-catalog.sh platxa-jwt-auth` |
| [platxa-secrets-management](skills/platxa-secrets-management/SKILL.md) | ![trust](badges/platxa-secrets-management.svg) | Fernet encryption, Kubernetes secrets, and secure token patterns for Platxa s... | security | Internal | 6,971 | Platxa | `./scripts/install-from-catalog.sh platxa-secrets-management` |
| [platxa-testing](skills/platxa-testing/SKILL.md) | ![trust](badges/platxa-testing.svg) | Automated testing patterns for Platxa platform using pytest, Vitest, and E2E ... | testing | Internal | 6,090 | Platxa | `./scripts/install-from-catalog.sh platxa-testing` |
| [test-generator](skills/test-generator/SKILL.md) | ![trust](badges/test-generator.svg) | Generate unit tests for existing code across Python, JavaScript/TypeScript, J... | testing | Internal | 3,392 | Platxa | `./scripts/install-from-catalog.sh test-generator` |
| [hugging-face-datasets](skills/hugging-face-datasets/SKILL.md) | ![trust](badges/hugging-face-datasets.svg) | Create and manage datasets on Hugging Face Hub. Supports initializing repos, ... | data | Essential | 4,034 | huggingface | `./scripts/install-from-catalog.sh hugging-face-datasets` |
| [hugging-face-evaluation](skills/hugging-face-evaluation/SKILL.md) | ![trust](badges/hugging-face-evaluation.svg) | Add and manage evaluation results in Hugging Face model cards. Supports extra... | data | Essential | 5,895 | huggingface | `./scripts/install-from-catalog.sh hugging-face-evaluation` |
| [hugging-face-model-trainer](skills/hugging-face-model-trainer/SKILL.md) | ![trust](badges/hugging-face-model-trainer.svg) | This skill should be used when users want to train or fine-tune language mode... | data | Essential | 23,224 | huggingface | `./scripts/install-from-catalog.sh hugging-face-model-trainer` |
| [systematic-debugging](skills/systematic-debugging/SKILL.md) | ![trust](badges/systematic-debugging.svg) | Use when encountering any bug, test failure, or unexpected behavior, before p... | debugging | Essential | 2,330 | Obra | `./scripts/install-from-catalog.sh systematic-debugging` |
| [figma](skills/figma/SKILL.md) | ![trust](badges/figma.svg) | Use the Figma MCP server to fetch design context, screenshots, variables, and... | design | Essential | 1,906 | openai | `./scripts/install-from-catalog.sh figma` |
| [figma-implement-design](skills/figma-implement-design/SKILL.md) | ![trust](badges/figma-implement-design.svg) | Translate Figma nodes into production-ready code with 1:1 visual fidelity usi... | design | Essential | 2,747 | openai | `./scripts/install-from-catalog.sh figma-implement-design` |
| [frontend-design](skills/frontend-design/SKILL.md) | ![trust](badges/frontend-design.svg) | Create distinctive, production-grade frontend interfaces with high design qua... | design | Essential | 1,084 | Anthropic | `./scripts/install-from-catalog.sh frontend-design` |
| [gh-fix-ci](skills/gh-fix-ci/SKILL.md) | ![trust](badges/gh-fix-ci.svg) | Use when a user asks to debug or fix failing GitHub PR checks that run in Git... | devtools | Essential | 893 | openai | `./scripts/install-from-catalog.sh gh-fix-ci` |
| [mcp-builder](skills/mcp-builder/SKILL.md) | ![trust](badges/mcp-builder.svg) | Guide for creating high-quality MCP (Model Context Protocol) servers that ena... | devtools | Essential | 1,922 | Anthropic | `./scripts/install-from-catalog.sh mcp-builder` |
| [docx](skills/docx/SKILL.md) | ![trust](badges/docx.svg) | Comprehensive document creation, editing, and analysis with support for track... | documents | Essential | 2,448 | Anthropic | `./scripts/install-from-catalog.sh docx` |
| [pdf](skills/pdf/SKILL.md) | ![trust](badges/pdf.svg) | Comprehensive PDF manipulation toolkit for extracting text and tables, creati... | documents | Essential | 1,804 | Anthropic | `./scripts/install-from-catalog.sh pdf` |
| [xlsx](skills/xlsx/SKILL.md) | ![trust](badges/xlsx.svg) | Comprehensive spreadsheet creation, editing, and analysis with support for fo... | documents | Essential | 2,650 | Anthropic | `./scripts/install-from-catalog.sh xlsx` |
| [react-best-practices](skills/react-best-practices/SKILL.md) | ![trust](badges/react-best-practices.svg) | React and Next.js performance optimization guidelines from Vercel Engineering... | frontend | Essential | 1,488 | Vercel | `./scripts/install-from-catalog.sh react-best-practices` |
| [web-artifacts-builder](skills/web-artifacts-builder/SKILL.md) | ![trust](badges/web-artifacts-builder.svg) | Suite of tools for creating elaborate, multi-component claude.ai HTML artifac... | frontend | Essential | 702 | Anthropic | `./scripts/install-from-catalog.sh web-artifacts-builder` |
| [using-git-worktrees](skills/using-git-worktrees/SKILL.md) | ![trust](badges/using-git-worktrees.svg) | Use when starting feature work that needs isolation from current workspace or... | git | Essential | 1,341 | Obra | `./scripts/install-from-catalog.sh using-git-worktrees` |
| [security-best-practices](skills/security-best-practices/SKILL.md) | ![trust](badges/security-best-practices.svg) | Perform language and framework specific security best-practice reviews and su... | security | Essential | 2,832 | openai | `./scripts/install-from-catalog.sh security-best-practices` |
| [playwright](skills/playwright/SKILL.md) | ![trust](badges/playwright.svg) | Use when the task requires automating a real browser from the terminal (navig... | testing | Essential | 1,969 | openai | `./scripts/install-from-catalog.sh playwright` |
| [test-driven-development](skills/test-driven-development/SKILL.md) | ![trust](badges/test-driven-development.svg) | Use when implementing any feature or bugfix, before writing implementation code | testing | Essential | 2,420 | Obra | `./scripts/install-from-catalog.sh test-driven-development` |
| [webapp-testing](skills/webapp-testing/SKILL.md) | ![trust](badges/webapp-testing.svg) | Toolkit for interacting with and testing local web applications using Playwri... | testing | Essential | 881 | Anthropic | `./scripts/install-from-catalog.sh webapp-testing` |
| [executing-plans](skills/executing-plans/SKILL.md) | ![trust](badges/executing-plans.svg) | Use when you have a written implementation plan to execute in a separate sess... | workflow | Essential | 562 | Obra | `./scripts/install-from-catalog.sh executing-plans` |
| [verification-before-completion](skills/verification-before-completion/SKILL.md) | ![trust](badges/verification-before-completion.svg) | Use when about to claim work is complete, fixed, or passing, before committin... | workflow | Essential | 987 | Obra | `./scripts/install-from-catalog.sh verification-before-completion` |
| [writing-plans](skills/writing-plans/SKILL.md) | ![trust](badges/writing-plans.svg) | Use when you have a spec or requirements for a multi-step task, before touchi... | workflow | Essential | 795 | Obra | `./scripts/install-from-catalog.sh writing-plans` |
| [atlas](skills/atlas/SKILL.md) | ![trust](badges/atlas.svg) | macOS-only AppleScript control for the ChatGPT Atlas desktop app. Use only wh... | backend | Useful | 910 | openai | `./scripts/install-from-catalog.sh atlas` |
| [backend-development](skills/backend-development/SKILL.md) | ![trust](badges/backend-development.svg) | Backend API design, database architecture, microservices patterns, and test-d... | backend | Useful | 882 | skillcreatorai | `./scripts/install-from-catalog.sh backend-development` |
| [database-design](skills/database-design/SKILL.md) | ![trust](badges/database-design.svg) | Database schema design, optimization, and migration patterns for PostgreSQL, ... | backend | Useful | 1,087 | skillcreatorai | `./scripts/install-from-catalog.sh database-design` |
| [llm-application-dev](skills/llm-application-dev/SKILL.md) | ![trust](badges/llm-application-dev.svg) | Building applications with Large Language Models - prompt engineering, RAG pa... | backend | Useful | 1,259 | skillcreatorai | `./scripts/install-from-catalog.sh llm-application-dev` |
| [python-development](skills/python-development/SKILL.md) | ![trust](badges/python-development.svg) | Modern Python development with Python 3.12+, Django, FastAPI, async patterns,... | backend | Useful | 798 | skillcreatorai | `./scripts/install-from-catalog.sh python-development` |
| [algorithmic-art](skills/algorithmic-art/SKILL.md) | ![trust](badges/algorithmic-art.svg) | Creating algorithmic art using p5.js with seeded randomness and interactive p... | design | Useful | 4,150 | Anthropic | `./scripts/install-from-catalog.sh algorithmic-art` |
| [web-design-guidelines](skills/web-design-guidelines/SKILL.md) | ![trust](badges/web-design-guidelines.svg) | Review UI code for Web Interface Guidelines compliance. Use when asked to "re... | design | Useful | 268 | Vercel | `./scripts/install-from-catalog.sh web-design-guidelines` |
| [best-practices](skills/best-practices/SKILL.md) | ![trust](badges/best-practices.svg) | Transforms vague prompts into optimized Claude Code prompts. Adds verificatio... | devtools | Useful | 5,308 | skillcreatorai | `./scripts/install-from-catalog.sh best-practices` |
| [code-documentation](skills/code-documentation/SKILL.md) | ![trust](badges/code-documentation.svg) | Writing effective code documentation - API docs, README files, inline comment... | devtools | Useful | 1,335 | skillcreatorai | `./scripts/install-from-catalog.sh code-documentation` |
| [code-refactoring](skills/code-refactoring/SKILL.md) | ![trust](badges/code-refactoring.svg) | Code refactoring patterns and techniques for improving code quality without c... | devtools | Useful | 1,273 | skillcreatorai | `./scripts/install-from-catalog.sh code-refactoring` |
| [code-review](skills/code-review/SKILL.md) | ![trust](badges/code-review.svg) | Automated code review for pull requests using specialized review patterns. An... | devtools | Useful | 672 | skillcreatorai | `./scripts/install-from-catalog.sh code-review` |
| [gh-address-comments](skills/gh-address-comments/SKILL.md) | ![trust](badges/gh-address-comments.svg) | Help address review/issue comments on the open GitHub PR for the current bran... | devtools | Useful | 282 | openai | `./scripts/install-from-catalog.sh gh-address-comments` |
| [hugging-face-cli](skills/hugging-face-cli/SKILL.md) | ![trust](badges/hugging-face-cli.svg) | Execute Hugging Face Hub operations using the `hf` CLI. Use when the user nee... | devtools | Useful | 3,767 | huggingface | `./scripts/install-from-catalog.sh hugging-face-cli` |
| [hugging-face-paper-publisher](skills/hugging-face-paper-publisher/SKILL.md) | ![trust](badges/hugging-face-paper-publisher.svg) | Publish and manage research papers on Hugging Face Hub. Supports creating pap... | devtools | Useful | 5,609 | huggingface | `./scripts/install-from-catalog.sh hugging-face-paper-publisher` |
| [hugging-face-tool-builder](skills/hugging-face-tool-builder/SKILL.md) | ![trust](badges/hugging-face-tool-builder.svg) | Use this skill when the user wants to build tool/scripts or achieve a task wh... | devtools | Useful | 1,209 | huggingface | `./scripts/install-from-catalog.sh hugging-face-tool-builder` |
| [jupyter-notebook](skills/jupyter-notebook/SKILL.md) | ![trust](badges/jupyter-notebook.svg) | Use when the user asks to create, scaffold, or edit Jupyter notebooks (`.ipyn... | devtools | Useful | 1,514 | openai | `./scripts/install-from-catalog.sh jupyter-notebook` |
| [linear](skills/linear/SKILL.md) | ![trust](badges/linear.svg) | Manage issues, projects & team workflows in Linear. Use when the user wants t... | devtools | Useful | 1,078 | openai | `./scripts/install-from-catalog.sh linear` |
| [openai-docs](skills/openai-docs/SKILL.md) | ![trust](badges/openai-docs.svg) | Use when the user asks how to build with OpenAI products or APIs and needs up... | devtools | Useful | 782 | openai | `./scripts/install-from-catalog.sh openai-docs` |
| [skill-creator](skills/skill-creator/SKILL.md) | ![trust](badges/skill-creator.svg) | Guide for creating effective skills. This skill should be used when users wan... | devtools | Useful | 4,188 | Anthropic | `./scripts/install-from-catalog.sh skill-creator` |
| [writing-skills](skills/writing-skills/SKILL.md) | ![trust](badges/writing-skills.svg) | Use when creating new skills, editing existing skills, or verifying skills wo... | devtools | Useful | 5,061 | Obra | `./scripts/install-from-catalog.sh writing-skills` |
| [doc](skills/doc/SKILL.md) | ![trust](badges/doc.svg) | Use when the task involves reading, creating, or editing `.docx` documents, e... | documents | Useful | 702 | openai | `./scripts/install-from-catalog.sh doc` |
| [pptx](skills/pptx/SKILL.md) | ![trust](badges/pptx.svg) | Presentation creation, editing, and analysis. When Claude needs to work with ... | documents | Useful | 6,197 | Anthropic | `./scripts/install-from-catalog.sh pptx` |
| [spreadsheet](skills/spreadsheet/SKILL.md) | ![trust](badges/spreadsheet.svg) | Use when tasks involve creating, editing, analyzing, or formatting spreadshee... | documents | Useful | 1,145 | openai | `./scripts/install-from-catalog.sh spreadsheet` |
| [composition-patterns](skills/composition-patterns/SKILL.md) | ![trust](badges/composition-patterns.svg) | React composition patterns that scale. Use when refactoring components with b... | frontend | Useful | 630 | Vercel | `./scripts/install-from-catalog.sh composition-patterns` |
| [javascript-typescript](skills/javascript-typescript/SKILL.md) | ![trust](badges/javascript-typescript.svg) | JavaScript and TypeScript development with ES6+, Node.js, React, and modern w... | frontend | Useful | 792 | skillcreatorai | `./scripts/install-from-catalog.sh javascript-typescript` |
| [changelog-generator](skills/changelog-generator/SKILL.md) | ![trust](badges/changelog-generator.svg) | Automatically creates user-facing changelogs from git commits by analyzing co... | git | Useful | 657 | skillcreatorai | `./scripts/install-from-catalog.sh changelog-generator` |
| [finishing-a-development-branch](skills/finishing-a-development-branch/SKILL.md) | ![trust](badges/finishing-a-development-branch.svg) | Use when implementation is complete, all tests pass, and you need to decide h... | git | Useful | 1,088 | Obra | `./scripts/install-from-catalog.sh finishing-a-development-branch` |
| [cloudflare-deploy](skills/cloudflare-deploy/SKILL.md) | ![trust](badges/cloudflare-deploy.svg) | Deploy applications and infrastructure to Cloudflare using Workers, Pages, an... | infrastructure | Useful | 2,482 | openai | `./scripts/install-from-catalog.sh cloudflare-deploy` |
| [hugging-face-jobs](skills/hugging-face-jobs/SKILL.md) | ![trust](badges/hugging-face-jobs.svg) | Run workloads on Hugging Face Jobs infrastructure. Covers UV scripts, Docker ... | infrastructure | Useful | 3,680 | huggingface | `./scripts/install-from-catalog.sh hugging-face-jobs` |
| [netlify-deploy](skills/netlify-deploy/SKILL.md) | ![trust](badges/netlify-deploy.svg) | Deploy web projects to Netlify using the Netlify CLI (`npx netlify`). Use whe... | infrastructure | Useful | 5,201 | openai | `./scripts/install-from-catalog.sh netlify-deploy` |
| [render-deploy](skills/render-deploy/SKILL.md) | ![trust](badges/render-deploy.svg) | Deploy applications to Render by analyzing codebases, generating render.yaml ... | infrastructure | Useful | 10,154 | openai | `./scripts/install-from-catalog.sh render-deploy` |
| [vercel-deploy](skills/vercel-deploy/SKILL.md) | ![trust](badges/vercel-deploy.svg) | Deploy applications and websites to Vercel using the bundled `scripts/deploy.... | infrastructure | Useful | 879 | openai | `./scripts/install-from-catalog.sh vercel-deploy` |
| [imagegen](skills/imagegen/SKILL.md) | ![trust](badges/imagegen.svg) | Use when the user asks to generate or edit images via the OpenAI Image API (f... | media | Useful | 8,933 | openai | `./scripts/install-from-catalog.sh imagegen` |
| [screenshot](skills/screenshot/SKILL.md) | ![trust](badges/screenshot.svg) | Use when the user explicitly asks for a desktop or system screenshot (full sc... | media | Useful | 1,916 | openai | `./scripts/install-from-catalog.sh screenshot` |
| [speech](skills/speech/SKILL.md) | ![trust](badges/speech.svg) | Use when the user asks for text-to-speech narration or voiceover, accessibili... | media | Useful | 4,995 | openai | `./scripts/install-from-catalog.sh speech` |
| [transcribe](skills/transcribe/SKILL.md) | ![trust](badges/transcribe.svg) | Transcribe audio files to text with optional diarization and known-speaker hi... | media | Useful | 842 | openai | `./scripts/install-from-catalog.sh transcribe` |
| [react-native-skills](skills/react-native-skills/SKILL.md) | ![trust](badges/react-native-skills.svg) | React Native and Expo best practices for building performant mobile apps. Use... | mobile | Useful | 1,041 | Vercel | `./scripts/install-from-catalog.sh react-native-skills` |
| [hugging-face-trackio](skills/hugging-face-trackio/SKILL.md) | ![trust](badges/hugging-face-trackio.svg) | Track and visualize ML training experiments with Trackio. Use when logging me... | observability | Useful | 3,533 | huggingface | `./scripts/install-from-catalog.sh hugging-face-trackio` |
| [sentry](skills/sentry/SKILL.md) | ![trust](badges/sentry.svg) | Use when the user asks to inspect Sentry issues or events, summarize recent p... | observability | Useful | 1,021 | openai | `./scripts/install-from-catalog.sh sentry` |
| [security-ownership-map](skills/security-ownership-map/SKILL.md) | ![trust](badges/security-ownership-map.svg) | Analyze git repositories to build a security ownership topology (people-to-fi... | security | Useful | 2,748 | openai | `./scripts/install-from-catalog.sh security-ownership-map` |
| [security-threat-model](skills/security-threat-model/SKILL.md) | ![trust](badges/security-threat-model.svg) | Repository-grounded threat modeling that enumerates trust boundaries, assets,... | security | Useful | 4,166 | openai | `./scripts/install-from-catalog.sh security-threat-model` |
| [qa-regression](skills/qa-regression/SKILL.md) | ![trust](badges/qa-regression.svg) | Automate QA regression testing with reusable test skills. Create login flows,... | testing | Useful | 2,089 | skillcreatorai | `./scripts/install-from-catalog.sh qa-regression` |
| [brainstorming](skills/brainstorming/SKILL.md) | ![trust](badges/brainstorming.svg) | You MUST use this before any creative work - creating features, building comp... | workflow | Useful | 522 | Obra | `./scripts/install-from-catalog.sh brainstorming` |
| [dispatching-parallel-agents](skills/dispatching-parallel-agents/SKILL.md) | ![trust](badges/dispatching-parallel-agents.svg) | Use when facing 2+ independent tasks that can be worked on without shared sta... | workflow | Useful | 1,405 | Obra | `./scripts/install-from-catalog.sh dispatching-parallel-agents` |
| [notion-knowledge-capture](skills/notion-knowledge-capture/SKILL.md) | ![trust](badges/notion-knowledge-capture.svg) | Capture conversations and decisions into structured Notion pages; use when tu... | workflow | Useful | 788 | openai | `./scripts/install-from-catalog.sh notion-knowledge-capture` |
| [notion-meeting-intelligence](skills/notion-meeting-intelligence/SKILL.md) | ![trust](badges/notion-meeting-intelligence.svg) | Prepare meeting materials with Notion context and Codex research; use when ga... | workflow | Useful | 812 | openai | `./scripts/install-from-catalog.sh notion-meeting-intelligence` |
| [notion-research-documentation](skills/notion-research-documentation/SKILL.md) | ![trust](badges/notion-research-documentation.svg) | Research across Notion and synthesize into structured documentation; use when... | workflow | Useful | 777 | openai | `./scripts/install-from-catalog.sh notion-research-documentation` |
| [notion-spec-to-implementation](skills/notion-spec-to-implementation/SKILL.md) | ![trust](badges/notion-spec-to-implementation.svg) | Turn Notion specs into implementation plans, tasks, and progress tracking; us... | workflow | Useful | 821 | openai | `./scripts/install-from-catalog.sh notion-spec-to-implementation` |
| [receiving-code-review](skills/receiving-code-review/SKILL.md) | ![trust](badges/receiving-code-review.svg) | Use when receiving code review feedback, before implementing suggestions, esp... | workflow | Useful | 1,513 | Obra | `./scripts/install-from-catalog.sh receiving-code-review` |
| [requesting-code-review](skills/requesting-code-review/SKILL.md) | ![trust](badges/requesting-code-review.svg) | Use when completing tasks, implementing major features, or before merging to ... | workflow | Useful | 642 | Obra | `./scripts/install-from-catalog.sh requesting-code-review` |
| [subagent-driven-development](skills/subagent-driven-development/SKILL.md) | ![trust](badges/subagent-driven-development.svg) | Use when executing implementation plans with independent tasks in the current... | workflow | Useful | 2,269 | Obra | `./scripts/install-from-catalog.sh subagent-driven-development` |
| [yeet](skills/yeet/SKILL.md) | ![trust](badges/yeet.svg) | Use only when the user explicitly asks to stage, commit, push, and open a Git... | devtools | Experimental | 411 | openai | `./scripts/install-from-catalog.sh yeet` |
| [develop-web-game](skills/develop-web-game/SKILL.md) | ![trust](badges/develop-web-game.svg) | Use when Codex is building or iterating on a web game (HTML/JS) and needs a r... | frontend | Experimental | 2,070 | openai | `./scripts/install-from-catalog.sh develop-web-game` |
| [slack-gif-creator](skills/slack-gif-creator/SKILL.md) | ![trust](badges/slack-gif-creator.svg) | Knowledge and utilities for creating animated GIFs optimized for Slack. Provi... | media | Experimental | 1,982 | Anthropic | `./scripts/install-from-catalog.sh slack-gif-creator` |
| [sora](skills/sora/SKILL.md) | ![trust](badges/sora.svg) | Use when the user asks to generate, remix, poll, list, download, or delete So... | media | Experimental | 8,517 | openai | `./scripts/install-from-catalog.sh sora` |
| [content-research-writer](skills/content-research-writer/SKILL.md) | ![trust](badges/content-research-writer.svg) | Assists in writing high-quality content by conducting research, adding citati... | workflow | Experimental | 3,400 | skillcreatorai | `./scripts/install-from-catalog.sh content-research-writer` |
| [using-superpowers](skills/using-superpowers/SKILL.md) | ![trust](badges/using-superpowers.svg) | Use when starting any conversation - establishes how to find and use skills, ... | workflow | Experimental | 925 | Obra | `./scripts/install-from-catalog.sh using-superpowers` |

---

## Categories

| Category | Skills | Description |
|----------|--------|-------------|
| backend | 8 | Server-side services and APIs |
| data | 3 |  |
| debugging | 1 | Bug diagnosis and resolution |
| design | 5 | UI/UX design and frontend aesthetics |
| devtools | 17 | Developer productivity tools |
| documents | 6 |  |
| frontend | 9 | Client-side components and UI |
| git | 5 | Git workflow automation |
| infrastructure | 7 | Kubernetes and cloud operations |
| media | 6 |  |
| mobile | 1 | Mobile app development |
| observability | 4 | Logging, monitoring, and tracing |
| odoo | 3 | Odoo ERP platform development |
| security | 5 | Authentication, encryption, secrets |
| testing | 6 | Test generation and automation |
| workflow | 14 | Agent workflow and orchestration |

---

## Skill Tiers

| Tier | Label | Description | Count |
|------|-------|-------------|-------|
| 0 | Internal | Platxa internal skills (local only) | 21 |
| 1 | Essential | Essential, high-quality skills | 22 |
| 2 | Useful | Useful, recommended skills | 51 |
| 3 | Experimental | Experimental or niche skills | 6 |

Install by tier: `./scripts/install-from-catalog.sh --all --tier 1`

---

## Installation Methods

### Method 1: Install Script (Recommended)

```bash
./scripts/install-from-catalog.sh <skill-name> [--user|--project]
```

| Flag | Description |
|------|-------------|
| `--user` | Install to `~/.claude/skills/` (default) |
| `--project` | Install to `.claude/skills/` |
| `--list` | List all available skills |
| `--all` | Install all skills |
| `--force` | Overwrite existing without prompting |
| `--tier N` | Only install skills with tier <= N |
| `--category X` | Only install skills matching category X |

### Method 2: Manual Copy

```bash
cp -r skills/<skill-name> ~/.claude/skills/
```

### Method 3: Symbolic Link (Development)

```bash
ln -s $(pwd)/skills/<skill-name> ~/.claude/skills/<skill-name>
```

---

## Quality Standards

All skills meet these requirements:

| Requirement | Threshold |
|-------------|-----------|
| SKILL.md exists | Required |
| Valid YAML frontmatter | Required |
| Name (hyphen-case) | <= 64 chars |
| Description | <= 1,024 chars |
| Token budget (SKILL.md) | <= 5,000 recommended |
| Token budget (total) | <= 15,000 recommended |
| All validations pass | Required |

```bash
# Validate a skill
./scripts/validate-all.sh skills/<skill-name>

# Check token count
python3 scripts/count-tokens.py skills/<skill-name>
```

---

## External vs Local Skills

- **Local** (21 skills): Created and maintained in this repo. Never overwritten by sync.
- **External** (79 skills): Synced from upstream repos (Anthropic, Vercel, Obra).

```bash
# Sync external skills from upstream
./scripts/sync-catalog.sh sync

# List sources
./scripts/sync-catalog.sh list-external
./scripts/sync-catalog.sh list-local
```

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full PR-based submission guide.

```bash
# Quick validation before submitting
./scripts/validate-all.sh skills/my-skill-name
python3 scripts/count-tokens.py skills/my-skill-name
python3 scripts/check-duplicates.py skills/my-skill-name
```

---

## License

MIT License - See [LICENSE](../LICENSE) for details.

---

*Auto-generated from registry data. 100 skills across 16 categories.*
