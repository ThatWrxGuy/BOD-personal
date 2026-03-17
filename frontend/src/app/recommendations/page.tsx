'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Lightbulb, Check, X, Clock, AlertTriangle } from 'lucide-react';

const recommendations = [
  {
    id: '1',
    title: 'Increase retirement savings by 5%',
    description: 'Based on your current savings rate and retirement goals, increasing your contribution would accelerate your timeline.',
    domain: 'Finance',
    confidence: 0.85,
    urgency: 3,
    status: 'pending',
    expectedImpact: 'High',
    tradeoff: 'Reduced disposable income',
  },
  {
    id: '2',
    title: 'Schedule weekly social connection time',
    description: 'Your relationship domain shows declining engagement. Regular social activities can improve overall well-being.',
    domain: 'Relationships',
    confidence: 0.72,
    urgency: 2,
    status: 'pending',
    expectedImpact: 'Medium',
    tradeoff: 'Time commitment',
  },
  {
    id: '3',
    title: 'Optimize sleep schedule',
    description: 'Health signals indicate irregular sleep patterns. Consistent sleep timing could improve energy and focus.',
    domain: 'Health',
    confidence: 0.78,
    urgency: 3,
    status: 'accepted',
    expectedImpact: 'High',
    tradeoff: 'Schedule adjustment',
  },
  {
    id: '4',
    title: 'Complete skill certification',
    description: 'Career advancement opportunity identified. Certification would strengthen your professional profile.',
    domain: 'Career',
    confidence: 0.65,
    urgency: 1,
    status: 'pending',
    expectedImpact: 'Medium',
    tradeoff: 'Learning time',
  },
];

function UrgencyBadge({ urgency }: { urgency: number }) {
  if (urgency >= 3) return <Badge variant="destructive">High</Badge>;
  if (urgency >= 2) return <Badge variant="warning">Medium</Badge>;
  return <Badge variant="secondary">Low</Badge>;
}

function StatusBadge({ status }: { status: string }) {
  const variants: Record<string, 'success' | 'secondary' | 'warning'> = {
    accepted: 'success',
    pending: 'secondary',
    rejected: 'warning',
  };
  return <Badge variant={variants[status] || 'secondary'}>{status}</Badge>;
}

export default function RecommendationsPage() {
  return (
    <div className="p-6 lg:p-8 space-y-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Recommendations</h1>
          <p className="text-muted-foreground mt-1">
            Strategic insights and actionable advice
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">Filter</Button>
          <Button variant="outline">Sort by Urgency</Button>
        </div>
      </div>

      <div className="grid gap-4">
        {recommendations.map((rec) => (
          <Card key={rec.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <Lightbulb className="w-5 h-5 text-yellow-500" />
                    <Badge variant="outline">{rec.domain}</Badge>
                    <UrgencyBadge urgency={rec.urgency} />
                    <StatusBadge status={rec.status} />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{rec.title}</h3>
                  <p className="text-muted-foreground mb-4">{rec.description}</p>
                  
                  <div className="flex items-center gap-6 text-sm">
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">Confidence:</span>
                      <span className="font-medium">{Math.round(rec.confidence * 100)}%</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">Expected Impact:</span>
                      <span className="font-medium">{rec.expectedImpact}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-yellow-500" />
                      <span className="text-muted-foreground">{rec.tradeoff}</span>
                    </div>
                  </div>
                </div>
                
                {rec.status === 'pending' && (
                  <div className="flex gap-2 ml-4">
                    <Button size="sm" variant="outline" className="gap-1">
                      <Clock className="w-4 h-4" />
                      Defer
                    </Button>
                    <Button size="sm" variant="outline" className="gap-1 text-red-500">
                      <X className="w-4 h-4" />
                      Reject
                    </Button>
                    <Button size="sm" className="gap-1">
                      <Check className="w-4 h-4" />
                      Approve
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
