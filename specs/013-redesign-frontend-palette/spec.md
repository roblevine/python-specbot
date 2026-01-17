# Feature Specification: Frontend Palette and Layout Redesign

**Feature Branch**: `013-redesign-frontend-palette`
**Created**: 2026-01-16
**Status**: Draft
**Input**: User description: "Radically redesign frontend look and feel with new color palette, centered chat layout, and refined UI elements"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visual Refresh with Warm Color Palette (Priority: P1)

A user opens the chat application and immediately sees a refreshed, modern interface using a warm, earthy color palette inspired by the provided design references. The interface feels cohesive, professional, and visually distinct from the previous blue/grey theme.

**Why this priority**: The color palette is the most visible and impactful change. It defines the overall aesthetic and brand feel of the application. Without this foundation, other layout changes would be inconsistent.

**Independent Test**: Can be fully tested by loading the application and verifying all color variables have been updated to the new warm palette (#FFDBBB, #CCBEB1, #997E67, #664930).

**Acceptance Scenarios**:

1. **Given** the user loads the application, **When** the interface renders, **Then** the main background uses a light cream color (#FFDBBB or derivative)
2. **Given** the user views any UI element, **When** checking text readability, **Then** text uses either black or white depending on background contrast (WCAG AA compliant)
3. **Given** the user views the sidebar, **When** it is expanded, **Then** it uses the same light cream background color as the main area (#FFDBBB)

---

### User Story 2 - Centered Chat Layout with System Responses as Main Content (Priority: P1)

A user sends a message and views the response. System (AI) responses appear in the center of the chat area as flowing content without bubble styling, while user messages appear on the right side with subtle styling. The conversation feels like reading a document with occasional input markers.

**Why this priority**: The layout change fundamentally alters how users read and interact with the chat. It's essential to the Claude-like experience requested.

**Independent Test**: Can be fully tested by sending a message and verifying system responses render centered without bubble backgrounds, and user messages render right-aligned with appropriate styling.

**Acceptance Scenarios**:

1. **Given** the system sends a response, **When** the message renders, **Then** the text appears centered in the chat area without a bubble background
2. **Given** the user sends a message, **When** the message renders, **Then** it appears right-aligned with a subtle background to distinguish it from system content
3. **Given** a conversation with multiple messages, **When** viewing the chat, **Then** system responses flow naturally as main content while user messages act as clear visual separators

---

### User Story 3 - Constrained Chat Width (Priority: P2)

A user on a wide monitor views the chat interface. The chat content area (messages and input box) is constrained to a comfortable reading width in the center of the screen, rather than stretching to fill the entire available space.

**Why this priority**: This improves readability on large screens and creates a more focused, professional appearance. It can be implemented after core layout changes.

**Independent Test**: Can be fully tested by resizing the browser window to various widths and verifying the chat area maintains a maximum width with centering on wider screens.

**Acceptance Scenarios**:

1. **Given** the browser window is wider than the maximum chat width, **When** viewing the chat, **Then** the chat content is centered horizontally with equal margins
2. **Given** the browser window is narrower than the maximum chat width, **When** viewing the chat, **Then** the chat content fills the available space appropriately
3. **Given** the input box at the bottom, **When** viewing on a wide screen, **Then** it is also constrained to the same maximum width as the chat messages

---

### User Story 4 - Refined Metadata Typography (Priority: P2)

A user views messages with metadata (timestamps, model indicators). This information appears in a smaller, more subtle font size that doesn't compete with the message content for visual attention.

**Why this priority**: Improves visual hierarchy and reduces clutter. Secondary to core layout changes.

**Independent Test**: Can be fully tested by viewing messages and verifying metadata text is visually subordinate to message content.

**Acceptance Scenarios**:

1. **Given** a message with a timestamp, **When** viewing the message, **Then** the timestamp appears in a smaller, lighter font than the message text
2. **Given** a system message with a model indicator, **When** viewing the message, **Then** the model name appears subtle and non-intrusive
3. **Given** any metadata element, **When** comparing to message content, **Then** the metadata is clearly secondary in visual hierarchy

---

### User Story 5 - Modest Button Styling (Priority: P2)

A user interacts with buttons in the interface (New Conversation, collapse sidebar, etc.). Buttons have a more understated, refined appearance that doesn't dominate the visual space.

**Why this priority**: Contributes to the overall refined aesthetic but doesn't affect core functionality.

**Independent Test**: Can be fully tested by viewing and interacting with buttons to verify subtle styling with clear hover/active states.

**Acceptance Scenarios**:

1. **Given** the "New Conversation" button, **When** viewing it, **Then** it appears subtle with a modest border or background
2. **Given** any button, **When** hovering over it, **Then** there is a clear but subtle visual feedback
3. **Given** any button, **When** it is focused or active, **Then** accessibility requirements are still met (visible focus indicator)

---

### User Story 6 - Improved Collapsed Sidebar Margin (Priority: P3)

A user collapses the sidebar. The expand icon/button has adequate margin from the edge of the collapsed sidebar, making it easier to click and visually balanced.

**Why this priority**: Minor visual polish that improves usability but is not critical to the redesign.

**Independent Test**: Can be fully tested by collapsing the sidebar and verifying the expand icon has appropriate padding/margin from the right edge.

**Acceptance Scenarios**:

1. **Given** the sidebar is collapsed, **When** viewing the expand button, **Then** it has visible margin from the right edge of the collapsed sidebar
2. **Given** the sidebar is collapsed, **When** clicking the expand button, **Then** the clickable area is easy to target
3. **Given** the sidebar transitions between collapsed/expanded, **When** observing the animation, **Then** the expand button position feels balanced

---

### Edge Cases

- What happens when a user message is very long? It should still display right-aligned with appropriate wrapping within the constrained width.
- What happens when a system response contains code blocks or formatted content? They should render within the centered flow without bubble styling.
- What happens on very narrow screens (mobile-like widths)? The layout should adapt gracefully, potentially removing width constraints.
- What happens with error messages? They should maintain visibility and error styling within the new color scheme.
- How does the streaming indicator appear in the new layout? It should be visible within the centered content flow.

## Requirements *(mandatory)*

### Functional Requirements

**Color Palette**
- **FR-001**: System MUST replace the current grey/blue color palette with the warm palette: #FFDBBB (light cream), #CCBEB1 (tan/taupe), #997E67 (warm brown), #664930 (dark brown)
- **FR-002**: System MUST use black (#000000 or near-black) text on light backgrounds (#FFDBBB, #CCBEB1) for readability
- **FR-003**: System MUST use white (#FFFFFF or near-white) text on dark backgrounds (#997E67, #664930) for readability
- **FR-004**: System MUST maintain WCAG AA contrast ratios (minimum 4.5:1 for normal text) for all text/background combinations

**Message Layout**
- **FR-005**: System MUST render system (AI) messages centered in the chat area without bubble backgrounds
- **FR-006**: System MUST render user messages right-aligned with a subtle distinguishing background
- **FR-007**: System MUST limit the chat content area to a maximum width of approximately 768px (estimated from reference screenshots)
- **FR-008**: System MUST center the constrained chat area horizontally when the viewport is wider than the maximum width
- **FR-009**: System MUST apply the same width constraint to the input/text entry area

**Typography and Metadata**
- **FR-010**: System MUST display metadata (timestamps, model indicators) in a font size smaller than the main message text
- **FR-011**: System MUST style metadata with reduced visual prominence (lighter color or reduced opacity)

**Button Styling**
- **FR-012**: System MUST style buttons with subtle borders or backgrounds that don't dominate the interface
- **FR-013**: System MUST maintain clear hover and focus states for accessibility

**Sidebar**
- **FR-014**: System MUST add additional margin/padding to the expand button when the sidebar is collapsed (minimum 8px from right edge)
- **FR-015**: System MUST update sidebar background color to match the main area (using --color-warm-cream instead of --color-warm-brown)

### Key Entities

- **Color Variables**: CSS custom properties that define the application's color scheme. Key attributes: name, hex value, usage context (background, text, accent).
- **Message Types**: User messages and system messages with distinct rendering styles. Key attributes: sender type, content, metadata (timestamp, model).
- **Layout Constraints**: Maximum widths and centering rules for content areas. Key attributes: max-width value, responsive breakpoints.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of color variables updated to the new warm palette with no remnants of the blue/grey theme
- **SC-002**: All text/background combinations meet WCAG AA contrast requirements (4.5:1 minimum)
- **SC-003**: System messages render without visible bubble backgrounds (no border-radius, no distinct background color)
- **SC-004**: User messages render right-aligned, distinguishable from system messages
- **SC-005**: Chat content maintains maximum width constraint on viewports wider than the constraint
- **SC-006**: All metadata text is visually smaller than message content text
- **SC-007**: Collapsed sidebar expand button has minimum 8px margin from right edge
- **SC-008**: All existing functionality (streaming, error display, conversation history) continues to work correctly
- **SC-009**: Application passes accessibility audit for color contrast and focus indicators

## Assumptions

- The application will use a single light theme (no dark mode support required for this feature)
- The exact maximum chat width (~768px) may be adjusted during implementation based on visual testing
- The reference screenshots from Claude.ai serve as the primary design inspiration
- Existing responsive behavior should be preserved for narrower viewports
- The StatusBar component color scheme should also be updated to match the new palette
