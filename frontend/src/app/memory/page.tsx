'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { BookOpen, Search, Tag, Calendar } from 'lucide-react';

const memories = [
  { id: '1', title: 'Q4 Goals Review', content: 'Completed major career milestones...', tags: ['Career', 'Goals'], date: '2024-01-15' },
  { id: '2', title: 'Investment Strategy Notes', content: 'Discussed portfolio rebalancing...', tags: ['Finance'], date: '2024-01-12' },
  { id: '3', title: 'Health Check Results', content: 'Annual physical showed improvements...', tags: ['Health'], date: '2024-01-10' },
];

export default function MemoryPage() {
  return (
    <div className="p-6 lg:p-8 space-y-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Memory</h1>
          <p className="text-muted-foreground mt-1">
            Your knowledge base and context continuity
          </p>
        </div>
        <Button variant="outline" className="gap-2">
          <Search className="w-4 h-4" />
          Search
        </Button>
      </div>

      <div className="grid gap-4">
        {memories.map((memory) => (
          <Card key={memory.id}>
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <BookOpen className="w-5 h-5 text-primary" />
                    <h3 className="font-semibold">{memory.title}</h3>
                  </div>
                  <p className="text-muted-foreground mb-3">{memory.content}</p>
                  <div className="flex items-center gap-3">
                    {memory.tags.map((tag) => (
                      <Badge key={tag} variant="outline" className="gap-1">
                        <Tag className="w-3 h-3" />
                        {tag}
                      </Badge>
                    ))}
                    <span className="text-sm text-muted-foreground flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {memory.date}
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
