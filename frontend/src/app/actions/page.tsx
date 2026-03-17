'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { CheckSquare, Clock, AlertCircle, ArrowRight } from 'lucide-react';
import Link from 'next/link';

const actions = [
  { id: '1', title: 'Complete weekly review', domain: 'Review', due: 'Today', status: 'pending', priority: 'high' },
  { id: '2', title: 'Update career goals', domain: 'Career', due: 'Tomorrow', status: 'pending', priority: 'medium' },
  { id: '3', title: 'Review Q1 budget', domain: 'Finance', due: 'Fri', status: 'pending', priority: 'medium' },
  { id: '4', title: 'Schedule health checkup', domain: 'Health', due: 'Mon', status: 'in_progress', priority: 'low' },
  { id: '5', title: 'Connect with mentor', domain: 'Career', due: 'Wed', status: 'completed', priority: 'low' },
];

function StatusIcon({ status }: { status: string }) {
  if (status === 'completed') return <CheckSquare className="w-5 h-5 text-green-500" />;
  if (status === 'in_progress') return <Clock className="w-5 h-5 text-blue-500" />;
  return <AlertCircle className="w-5 h-5 text-yellow-500" />;
}

export default function ActionsPage() {
  return (
    <div className="p-6 lg:p-8 space-y-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Action Center</h1>
          <p className="text-muted-foreground mt-1">
            Track and complete your pending actions
          </p>
        </div>
        <Button>Add Action</Button>
      </div>

      <div className="grid gap-4">
        {actions.map((action) => (
          <Card key={action.id}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <StatusIcon status={action.status} />
                  <div>
                    <p className="font-medium">{action.title}</p>
                    <div className="flex items-center gap-3 mt-1">
                      <Badge variant="outline">{action.domain}</Badge>
                      <span className="text-sm text-muted-foreground">Due: {action.due}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={action.status === 'completed' ? 'success' : action.status === 'in_progress' ? 'info' : 'secondary'}>
                    {action.status}
                  </Badge>
                  {action.status !== 'completed' && (
                    <Button size="sm">Complete</Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
