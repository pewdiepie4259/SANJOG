import React from 'react';
import { createRoot } from 'react-dom/client';
import { DonorAiMatchWidget } from './DonorAiMatchWidget';
import { LiveCourierTrackerWidget } from './LiveCourierTrackerWidget';

export function mountReactWidgets(): void {
  // 1. Mount Donor AI Matcher widget if target container exists
  const aiMatchContainer = document.getElementById('react-donor-ai-root');
  if (aiMatchContainer) {
    const root = createRoot(aiMatchContainer);
    root.render(<DonorAiMatchWidget />);
  }

  // 2. Mount Live Courier Tracker widget if target container exists
  const courierTrackerContainer = document.getElementById('react-courier-tracker-root');
  if (courierTrackerContainer) {
    const root = createRoot(courierTrackerContainer);
    root.render(<LiveCourierTrackerWidget />);
  }
}

// Auto-mount on DOM ready
if (typeof window !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountReactWidgets);
  } else {
    mountReactWidgets();
  }
}
