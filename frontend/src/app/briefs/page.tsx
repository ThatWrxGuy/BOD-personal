'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { FileText, Calendar, ChevronRight, Target, AlertCircle } from 'lucide-react';

const briefs = [
  {
    id: '1',
    title: 'Executive Brief - Week 3, 2024',
    date: '2024-01-15',
    status: 'current',
    posture: 'neutral',
    readinessScore: 85,
    riskAlerts: 2,
  },
  {
    id: '2',
    title: 'Executive Brief - Week 2, 2024',
    date: '2024-01-08',
    status: 'archived',
    posture: 'offensive',
    readinessScore: 82,
    riskAlerts: 1,
  },
  {
    id: '3',
    title: 'Executive Brief - Week 1, 2024',
    date: '2024-01-01',
    status: 'archived',
    posture: 'defensive',
    readinessScore: 68,
    riskAlerts: 4,
  },
];

export default function BriefsPage() {
  return (
    <div className="p-6 lg:p-8 space-y-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Executive Briefs</h1>
          <p className="text-muted-foreground mt-1">
            Strategic intelligence reports for your life
          </p>
        </div>
        <Button>Generate New Brief</Button>
      </div>

      {/* Current Brief */}
      <Card className="border-primary">
        <CardHeader className="bg-primary/5">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Current Brief
              </CardTitle>
              <CardDescription>{briefs[0].title}</CardDescription>
            </div>
            <Badge variant="default">Active</Badge>
          </div>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="grid gap-4 md:grid-cols-4">
            <div className="flex items-center gap-3">
              <Target className="w-5 h-5 text-blue-500" />
              <div>
                <p className="text-sm text-muted-foreground">Posture</p>
                <p className="font-semibold capitalize">{briefs[0].posture}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-5 h-5 flex items-center justify-center text-purple-500 font-bold">%</div>
              <div>
                <p className="text-sm text-muted-foreground">Readiness</p>
                <p className="font-semibold">{briefs[0].readinessScore}%</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-500" />
              <div>
                <p className="text-sm text-muted-foreground">Risk Alerts</p>
                <p className="font-semibold">{briefs[0].riskAlerts}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Calendar className="w-5 h-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Generated</p>
                <p className="font-semibold">{briefs[0].date}</p>
              </div>
            </div>
          </div>
          <Button className="w-full mt-6">View Full Brief</Button>
        </CardContent>
      </Card>

      {/* Brief History */}
      <Card>
        <CardHeader>
          <CardTitle>Brief History</CardTitle>
          <CardDescription>Previous executive intelligence reports</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {briefs.slice(1).map((brief) => (
              <div
                key={brief.id}
                className="flex items-center justify-between p-4 rounded-lg border hover:bg-muted/50 cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-4">
                  <FileText className="w-5 h-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">{brief.title}</p>
                    <div className="flex items-center gap-3 mt-1">
                      <Badge variant="outline" className="capitalize">{brief.posture}</Badge>
                      <span className="text-sm text-muted-foreground">{brief.date}</span>
                    </div>
                  </div>
                </div>
                <ChevronRight className="w-5 h-5 text-muted-foreground" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
