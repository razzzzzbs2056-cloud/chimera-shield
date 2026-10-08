---
name: design-md-catalog
description: Pick a ready-made DESIGN.md visual style (68 brand-inspired design systems such as Vercel, Linear, Stripe, Sentry, Supabase) and apply it to this project's UI. Use when the user wants a look "like <brand>", asks for a design system, theme, or style direction, or wants to create or replace the project's DESIGN.md.
---

# DESIGN.md Catalog

A `DESIGN.md` is one markdown file describing a visual language: color tokens, type scale, spacing, components, and the reasoning behind them. This skill wraps the curated list from VoltAgent/awesome-claude-design.

## Workflow

1. **Check for an existing `DESIGN.md`** at the repo root. If one exists, follow it and only replace it when the user asks.
2. **Pick a style.** Read `catalog.md` (in this skill's folder). Match the user's brand name or described feel (e.g. "dark, data-dense, security dashboard") to 1-3 entries and say why. If the user named a brand, use it directly.
3. **Fetch it.** Open the entry's `https://getdesign.md/<slug>/design-md` page with WebFetch and pull out the DESIGN.md content. If the host is blocked or the page has no extractable markdown, ask the user to download it from that link and paste it or drop it in the repo.
4. **Save it** as `DESIGN.md` at the repo root, adding a first line noting the source URL.
5. **Apply it.** When building UI, map the file's tokens onto the project's styling system (CSS variables, Tailwind theme, etc.) rather than hard-coding values, and keep later screens on-system.

## Notes

- These styles are inspired by real brands. Use them as a visual direction; do not copy logos, brand names, or trademarked assets into this product.
- If the user wants to use the file in Claude Design (claude.ai/design) instead: create a new design system and upload `DESIGN.md` under "Add assets", or attach it to a prototype chat with "Create a design system from this DESIGN.md".
