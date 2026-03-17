'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Globe, TrendingUp, TrendingDown, Minus, ArrowRight } from 'lucide-react';
import Link from 'next/link';

const domains = [
  {
    id: 'finance',
    name: 'Finance',
    description: 'Financial health, investments, and wealth building',
    score: 78,
    trend: 'up',
    status: 'healthy',
    activeRecommendations: 3,
    pendingActions: 2,
  },
  {
    id: 'health',
    name: 'Health',
    description: 'Physical and mental well-being',
    score: 65,
    trend: 'down',
    status: 'caution',
    activeRecommendations: 2,
    pendingActions: 1,
  },
  {
    id: 'career',
    name: 'Career',
    description: 'Professional growth and income',
    score: 82,
    trend: 'up',
    status: 'healthy',
    activeRecommendations: 1,
    pendingActions: 3,
  },
  {
    id: 'relationships',
    name: 'Relationships',
    description: 'Personal connections and social health',
    score: 71,
    trend: 'stable',
    status: 'healthy',
    activeRecommendations: 2,
    pendingActions: 0,
  },
  {
    id: 'intelligence',
    name: 'Intelligence',
    description: 'Knowledge and cognitive development',
    score: 58,
    trend: 'down',
    status: 'caution',
    activeRecommendations: 4,
    pendingActions: 2,
  },
  {
    id: 'life-architecture',
    name: 'Life Architecture',
    description: 'Life design and long-term planning',
    score: 73,
    trend: 'up',
    status: 'healthy',
    activeRecommendations: 1,
    pendingActions: 1,
  },
];

function TrendIcon({ trend }: { trend: string }) {
  if (trend === 'up') return <TrendingUp className="w-5 h-5 text-green-500" />;
  if (trend === 'down') return <TrendingDown className="w-5 h-5 text-red-500" />;
  return <Minus className="w-5 h-5 text-gray-400" />;
}

function StatusBadge({ status }: { status: string }) {
  const variants: Record<string, 'success' | 'warning' | 'destructive' | 'secondary'> = {
    healthy: 'success',
    caution: 'warning',
    critical: 'destructive',
  };
  return <Badge variant={variants[status] || 'secondary'}>{status}</Badge>;
}

export default function DomainsPage() {
  return (
    <div className="p-6 lg:p-8 space-y-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Life Domains</h1>
          <p className="text-muted-foreground mt-1">
            Monitor and manage all aspects of your life
          </p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {domains.map((domain) => (
          <Link key={domain.id} href={`/domains/${domain.id}`}>
            <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <Globe className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{domain.name}</CardTitle>
                      <StatusBadge status={domain.status} />
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-3xl font-bold">{domain.score}</span>
                    <TrendIcon trend={domain.trend} />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="mb-4">{domain.description}</CardDescription>
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-4">
                    <span className="text-muted-foreground">
                      <Badge variant="outline" className="mr-1">{domain.activeRecommendations}</Badge> recommendations
                    </span>
                    <span className="text-muted-foreground">
                      <Badge variant="outline" className="mr-1">{domain.pendingActions}</Badge> actions
                    </span>
                  </div>
                  <ArrowRight className="w-4 h-4 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
