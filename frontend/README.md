# Busy Bee Frontend

## BB-APP-001 Phase 4: Executive Frontend & Operator Experience

This is the frontend application for Busy Bee - Your Personal Life Operating System.

### Tech Stack

- **Framework**: Next.js 14
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **Components**: Radix UI primitives
- **State**: Zustand + TanStack Query
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts

### Getting Started

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── dashboard/          # Executive dashboard
│   │   ├── domains/            # Domain overview & details
│   │   ├── recommendations/    # Recommendations workspace
│   │   ├── actions/            # Action center
│   │   ├── memory/             # Memory timeline
│   │   ├── reviews/            # Review cycles
│   │   ├── briefs/             # Executive briefs
│   │   ├── settings/           # Settings pages
│   │   └── login/              # Authentication
│   ├── components/             # Reusable UI components
│   │   ├── ui/                 # Base UI primitives
│   │   ├── charts/             # Chart components
│   │   └── navigation/         # Navigation components
│   ├── lib/                    # Utilities and helpers
│   │   ├── api/                # API clients
│   │   └── utils.ts            # Utility functions
│   ├── hooks/                  # Custom React hooks
│   └── store/                  # State management
├── public/                    # Static assets
└── package.json
```

### Design System

The project uses a custom design system built on:
- Tailwind CSS with CSS variables
- Radix UI for accessible primitives
- Lucide React for icons

### Features

- Executive Dashboard with system status
- Domain health overview
- Recommendations workspace
- Action center with tracking
- Memory timeline
- Review cycles
- Executive briefs viewer
- Settings management

### Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_USE_MOCK_AUTH=true
```

### Development

```bash
# Run linting
npm run lint

# Run tests
npm run test

# Run Storybook
npm run storybook
```

### BB-APP-001 Compliance

This frontend implements Phase 4 of BB-APP-001:
- Layered modular architecture
- Executive dashboard
- Domain management
- Recommendations workspace
- Action center
- Memory & reviews
- Settings & configuration

### Future Phases

- Phase 4E: Hardening (testing, accessibility, performance)
- Mobile responsive optimization
- Telemetry integration
