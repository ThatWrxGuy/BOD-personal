/**
 * TimelineEvent - displays financial history events in timeline format
 */

import React from 'react';
import { format } from 'date-fns';
import { 
  Camera, 
  FileText, 
  Play, 
  Send, 
  CheckCircle, 
  Briefcase,
  DollarSign
} from 'lucide-react';

const TimelineEvent = ({ event }) => {
  const { timestamp, event_type, description, event_reference, profile_id } = event;

  const getEventIcon = () => {
    switch (event_type) {
      case 'snapshot_created':
        return <Camera className="w-4 h-4" />;
      case 'recommendation_generated':
        return <FileText className="w-4 h-4" />;
      case 'simulation_run':
        return <Play className="w-4 h-4" />;
      case 'decision_requested':
        return <Send className="w-4 h-4" />;
      case 'decision_resolved':
        return <CheckCircle className="w-4 h-4" />;
      case 'board_brief_generated':
        return <Briefcase className="w-4 h-4" />;
      default:
        return <DollarSign className="w-4 h-4" />;
    }
  };

  const getEventColor = () => {
    switch (event_type) {
      case 'snapshot_created':
        return 'bg-blue-100 text-blue-600';
      case 'recommendation_generated':
        return 'bg-purple-100 text-purple-600';
      case 'simulation_run':
        return 'bg-orange-100 text-orange-600';
      case 'decision_requested':
        return 'bg-yellow-100 text-yellow-600';
      case 'decision_resolved':
        return 'bg-green-100 text-green-600';
      case 'board_brief_generated':
        return 'bg-indigo-100 text-indigo-600';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const formatEventType = (type) => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatTimestamp = (ts) => {
    if (!ts) return 'Unknown';
    try {
      const date = new Date(ts);
      return format(date, 'MMM dd, yyyy HH:mm');
    } catch {
      return ts;
    }
  };

  return (
    <div className="flex gap-4 py-3">
      <div className={`p-2 rounded-full ${getEventColor()} flex-shrink-0`}>
        {getEventIcon()}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1">
          <span className="font-medium text-gray-900">{formatEventType(event_type)}</span>
          <span className="text-xs text-gray-500">{formatTimestamp(timestamp)}</span>
        </div>
        <p className="text-sm text-gray-600">{description}</p>
        {event_reference && (
          <span className="text-xs text-gray-400 mt-1 block">Ref: {event_reference}</span>
        )}
      </div>
    </div>
  );
};

export default TimelineEvent;
