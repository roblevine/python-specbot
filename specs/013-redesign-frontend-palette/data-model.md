# Data Model: Frontend Palette and Layout Redesign

**Feature**: 013-redesign-frontend-palette
**Date**: 2026-01-16

## Overview

This feature involves CSS/styling changes only. There are no traditional data entities to model. This document defines the **CSS variable mappings** that serve as the "data model" for the visual design system.

## CSS Variable Mappings

### Color Palette Variables

| Variable Name | Old Value | New Value | Purpose |
|---------------|-----------|-----------|---------|
| `--color-warm-cream` | N/A (new) | #FFDBBB | Main background |
| `--color-warm-tan` | N/A (new) | #CCBEB1 | User message bubbles |
| `--color-warm-brown` | N/A (new) | #997E67 | Sidebar background |
| `--color-warm-dark` | N/A (new) | #664930 | Accents, dark elements |

### Mapped Semantic Variables

| Semantic Variable | Old Value | New Value | Notes |
|-------------------|-----------|-----------|-------|
| `--color-background` | #f5f5f7 | var(--color-warm-cream) | Main app background |
| `--color-surface` | #ffffff | var(--color-warm-cream) | Content surfaces |
| `--color-text` | #1d1d1f | #1d1d1f | Keep near-black |
| `--color-text-secondary` | #86868b | #664930 | Dark brown for metadata |
| `--color-border` | #d1d1d6 | var(--color-warm-brown) | Borders/dividers |
| `--color-user-message-bg` | #a8c9e8 | var(--color-warm-tan) | User bubble |
| `--color-user-message-text` | #1d1d1f | #1d1d1f | Keep dark |
| `--color-system-message-bg` | #ffffff | transparent | No bubble |
| `--color-system-message-text` | #1d1d1f | #1d1d1f | Keep dark |
| `--color-sidebar-bg` | N/A (new) | var(--color-warm-brown) | Sidebar background |
| `--color-sidebar-text` | N/A (new) | #1d1d1f | Dark text on warm brown |

### Layout Variables

| Variable Name | Old Value | New Value | Purpose |
|---------------|-----------|-----------|---------|
| `--chat-max-width` | N/A (new) | 768px | Chat content constraint |
| `--font-size-xs` | N/A (new) | 0.75rem | Metadata font size |
| `--collapsed-sidebar-margin` | N/A (new) | 12px | Expand button margin |

### Variables to Remove (Legacy)

| Variable | Reason |
|----------|--------|
| `--color-grey-bg` | Replaced by warm palette |
| `--color-grey-surface` | Replaced by warm palette |
| `--color-grey-border` | Replaced by warm palette |
| `--color-blue-primary` | Replaced by warm palette |
| `--color-blue-hover` | Replaced by warm palette |
| `--color-blue-light` | Replaced by warm palette |

## Component Style Mappings

### MessageBubble.vue

| Element | Current Style | New Style |
|---------|---------------|-----------|
| System message container | Background, border-radius, padding | Transparent, no radius, minimal padding |
| System message alignment | flex-start (left) | Centered within constrained container |
| User message container | Background #a8c9e8 | Background var(--color-warm-tan) |
| User message alignment | flex-end (right) | flex-end (right), max-width 80% |

### ChatArea.vue

| Element | Current Style | New Style |
|---------|---------------|-----------|
| Messages container | Full width | max-width: var(--chat-max-width), centered |

### InputArea.vue

| Element | Current Style | New Style |
|---------|---------------|-----------|
| Input container | Full width | max-width: var(--chat-max-width), centered |
| Send button | Prominent styling | Ghost/outline button |

### HistoryBar.vue

| Element | Current Style | New Style |
|---------|---------------|-----------|
| Sidebar background | var(--color-surface) | var(--color-sidebar-bg) |
| Sidebar text | var(--color-text) | var(--color-sidebar-text) |
| Collapsed expand button margin | ~0-4px from edge | var(--collapsed-sidebar-margin) |
| New Conversation button | Prominent box-shadow | Ghost/outline styling |

### StatusBar.vue / ModelSelector.vue

| Element | Current Style | New Style |
|---------|---------------|-----------|
| Metadata text | var(--font-size-sm) | var(--font-size-xs) |
| Metadata color | var(--color-text) | var(--color-text-secondary) |

## WCAG Compliance Matrix

| Background | Text | Contrast | Status |
|------------|------|----------|--------|
| #FFDBBB (cream) | #1d1d1f (near-black) | 13.01:1 | ✅ AA Pass |
| #CCBEB1 (tan) | #1d1d1f (near-black) | 9.39:1 | ✅ AA Pass |
| #997E67 (brown) | #1d1d1f (near-black) | ~4.8:1 | ✅ AA Pass |
| #664930 (dark) | #FFFFFF (white) | 8.33:1 | ✅ AA Pass |

**Note**: White text on #997E67 (warm brown) fails at 3.80:1. Use dark text instead.
