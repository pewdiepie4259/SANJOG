import { AngularTelemetryAuditor } from './telemetry.component';
import { AngularPassportAuditor } from './passport.component';

export function mountAngularWidgets(): void {
  const telemetryContainer = document.getElementById('angular-telemetry-root');
  if (telemetryContainer) {
    new AngularTelemetryAuditor(telemetryContainer);
  }

  const passportContainer = document.getElementById('angular-passport-root');
  if (passportContainer) {
    new AngularPassportAuditor(passportContainer);
  }
}

// Auto-mount on DOM ready
if (typeof window !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountAngularWidgets);
  } else {
    mountAngularWidgets();
  }
}
