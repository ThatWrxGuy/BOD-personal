'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  LayoutDashboard,
  TrendingUp,
  TrendingDown,
  Minus,
  AlertCircle,
  CheckCircle2,
  Clock,
  ArrowRight,
  FileText,
  Globe,
  Lightbulb,
  Target,
} from 'lucide-react';
import Link from 'next/link';

// Mock data - will be replaced with API calls
const mockSystemStatus = {
  status: 'healthy' as const,
  posture: 'neutral' as const,
  readinessScore: 85,
  lastUpdated: new Date().toISOString(),
};

const mockDomainHealth = [
  { domain: 'Finance', score: 78, trend: 'up', status: 'healthy' },
  { domain: 'Health', score: 65, trend: 'down', status: 'caution' },
  { domain: 'Career', score: 82, trend: 'up', status: 'healthy' },
  { domain: 'Relationships', score: 71, trend: 'stable', status: 'healthy' },
  { domain: 'Intelligence', score: 58, trend: 'down', status: 'caution' },
  { domain: 'Life Architecture', score: 73, trend: 'up', status: 'healthy' },
];

const mockPriorities = [
  { id: '1', title: 'Complete quarterly career review', domain: 'Career', urgency: 'high' },
  { id: '2', title: 'Schedule health checkup', domain: 'Health', urgency: 'medium' },
  { id: '3', title: 'Review investment rebalancing', domain: 'Finance', urgency: 'low' },
];

const mockRecommendations = [
  {
    id: '1',
    title: 'Increase retirement savings by 5%',
    domain: 'Finance',
    confidence: 0.85,
    urgency: 3,
  },
  {
    id: '2',
    title: 'Schedule weekly social connection time',
    domain: 'Relationships',
    confidence: 0.72,
    urgency: 2,
  },
];

const mockPendingActions = [
  { id: '1', title: 'Complete weekly review', due: 'Today', status: 'pending' },
  { id: '2', title: 'Update career goals', due: 'Tomorrow', status: 'pending' },
  { id: '3', title: 'Review Q1 budget', due: 'Fri', status: 'pending' },
];

function TrendIcon({ trend }: { trend: string }) {
  if (trend === 'up') return <TrendingUp className="w-4 h-4 text-green-500" />;
  if (trend === 'down') return <TrendingDown className="w-4 h-4 text-red-500" />;
  return <Minus className="w-4 h-4 text-gray-400" />;
}

function StatusBadge({ status }: { status: string }) {
  const variants: Record<string, 'success' | 'warning' | 'destructive' | 'secondary'> = {
    healthy: 'success',
    caution: 'warning',
    critical: 'destructive',
  };
  return <Badge variant={variants[status] || 'secondary'}>{status}</Badge>;
}

function UrgencyBadge({ urgency }: { urgency: string }) {
  const variants: Record<string, 'destructive' | 'warning' | 'secondary'> = {
    high: 'destructive',
    medium: 'warning',
    low: 'secondary',
  };
  return <Badge variant={variants[urgency] || 'secondary'}>{urgency}</Badge>;
}

export default function DashboardPage() {
  return (
    <div className="p-6 lg:p-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Executive Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Your Life Operating System at a glance
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline">
            <Clock className="w-4 h-4 mr-2" />
            Last updated: {new Date().toLocaleTimeString()}
          </Button>
          <Button>
            <FileText className="w-4 h-4 mr-2" />
            View Brief
          </Button>
        </div>
      </div>

      {/* System Status */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Status</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">Healthy</div>
            <p className="text-xs text-muted-foreground">All systems operational</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Posture</CardTitle>
            <Target className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold capitalize">{mockSystemStatus.posture}</div>
            <p className="text-xs text-muted-foreground">Current strategic stance</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Readiness Score</CardTitle>
            <LayoutDashboard className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockSystemStatus.readinessScore}%</div>
            <p className="text-xs text-muted-foreground">+5% from last week</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
            <AlertCircle className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2</div>
            <p className="text-xs text-muted-foreground">Requiring attention</p>
          </CardContent>
        </Card>
      </div>

      {/* Domain Health */}
      <Card>
        <CardHeader>
          <CardTitle>Domain Health Overview</CardTitle>
          <CardDescription>Current state across all life domains</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {mockDomainHealth.map((domain) => (
              <Link
                key={domain.domain}
                href={`/domains/${domain.domain.toLowerCase()}`}
                className="flex items-center justify-between p-4 rounded-lg border hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Globe className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">{domain.domain}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <StatusBadge status={domain.status} />
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-2xl font-bold">{domain.score}</span>
                  <TrendIcon trend={domain.trend} />
                </div>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Priorities */}
        <Card>
          <CardHeader className="flex flex-row items-center">
            <div className="flex-1">
              <CardTitle>Top Priorities</CardTitle>
              <CardDescription>What needs your attention now</CardDescription>
            </div>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/recommendations">
                View all <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockPriorities.map((priority) => (
                <div
                  key={priority.id}
                  className="flex items-center justify-between p-3 rounded-lg border"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-primary" />
                    <div>
                      <p className="font-medium">{priority.title}</p>
                      <p className="text-sm text-muted-foreground">{priority.domain}</p>
                    </div>
                  </div>
                  <UrgencyBadge urgency={priority.urgency} />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Pending Actions */}
        <Card>
          <CardHeader className="flex flex-row items-center">
            <div className="flex-1">
              <CardTitle>Action Queue</CardTitle>
              <CardDescription>Pending tasks from recommendations</CardDescription>
            </div>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/actions">
                View all <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockPendingActions.map((action) => (
                <div
                  key={action.id}
                  className="flex items-center justify-between p-3 rounded-lg border"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-5 h-5 rounded-full border-2 border-primary" />
                    <div>
                      <p className="font-medium">{action.title}</p>
                      <p className="text-sm text-muted-foreground">Due: {action.due}</p>
                    </div>
                  </div>
                  <Button size="sm">Complete</Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recommendations Spotlight */}
      <Card>
        <CardHeader className="flex flex-row items-center">
          <div className="flex-1">
            <CardTitle>Strategic Recommendations</CardTitle>
            <CardDescription>AI-generated insights for your consideration</CardDescription>
          </div>
          <Button variant="ghost" size="sm" asChild>
            <Link href="/recommendations">
              View all <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            {mockRecommendations.map((rec) => (
              <div
                key={rec.id}
                className="p-4 rounded-lg border hover:shadow-md transition-shadow cursor-pointer"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Lightbulb className="h-5 w-5 text-yellow-500" />
                    <Badge variant="outline">{rec.domain}</Badge>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {Math.round(rec.confidence * 100)}% confidence
                  </div>
                </div>
                <p className="font-medium">{rec.title}</p>
                <div className="mt-4 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">Urgency:</span>
                    <UrgencyBadge urgency={rec.urgency === 3 ? 'high' : rec.urgency === 2 ? 'medium' : 'low'} />
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline">Defer</Button>
                    <Button size="sm">Approve</Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
