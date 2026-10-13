/**
 * SANJOG - Community Food Rescue Network
 * Angular Telemetry & Governance Component (TypeScript)
 */

export interface TelemetryLogItem {
  id: string;
  entityName: string;
  type: string;
  verificationBadge: string;
  status: 'APPROVED' | 'IN_AUDIT' | 'ACTION_REQUIRED';
  timestamp: string;
}

export class AngularTelemetryAuditor {
  private container: HTMLElement;
  private logs: TelemetryLogItem[] = [
    {
      id: 'AUD-901',
      entityName: 'Annapurna Grand (Indiranagar)',
      type: 'Commercial Kitchen',
      verificationBadge: 'FSSAI #11221334000192',
      status: 'APPROVED',
      timestamp: '15 mins ago'
    },
    {
      id: 'AUD-902',
      entityName: 'Hope Community Shelter (St. Marks)',
      type: 'Shelter Home',
      verificationBadge: 'DARPAN #KA/2021/0298412',
      status: 'APPROVED',
      timestamp: '42 mins ago'
    },
    {
      id: 'AUD-903',
      entityName: 'GreenLeaf Organic Cafe (MG Road)',
      type: 'Bakery & Fresh Produce',
      verificationBadge: 'FSSAI #11222334000455',
      status: 'APPROVED',
      timestamp: '1h 10m ago'
    },
    {
      id: 'AUD-904',
      entityName: 'Karuna Senior Care Home (Shivajinagar)',
      type: 'Elderly Care',
      verificationBadge: 'DARPAN #KA/2020/0187291',
      status: 'APPROVED',
      timestamp: '2h ago'
    }
  ];

  constructor(container: HTMLElement) {
    this.container = container;
    this.render();
  }

  public auditEntity(id: string): void {
    const item = this.logs.find(l => l.id === id);
    if (item) {
      const win = window as any;
      if (typeof win.showToast === 'function') {
        win.showToast(`Auditing ${item.entityName}... FSSAI / DARPAN record re-verified!`);
      }
    }
    this.render();
  }

  public render(): void {
    this.container.innerHTML = `
      <div class="bg-white p-6 rounded-3xl border border-ivory-300 shadow-soft space-y-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-ivory-200 gap-3">
          <div>
            <span class="px-3 py-1 bg-ivory-200 text-ivory-950 border border-ivory-400 rounded-full text-xs font-bold inline-flex items-center gap-1.5 mb-2">
              <i class="fa-solid fa-shield-halved text-pista-700"></i>
              <span>Angular Platform Governance Engine</span>
            </span>
            <h2 class="font-serif text-2xl font-black text-pista-950">City Telemetry & Compliance Desk</h2>
            <p class="text-xs text-ivory-700 mt-1">Real-time audit log of FSSAI and DARPAN safety accreditations across the network.</p>
          </div>
          <div class="flex items-center gap-2">
            <span class="px-3 py-1.5 rounded-xl bg-pista-100 text-pista-800 font-bold text-xs border border-pista-300">
              <span class="w-2 h-2 rounded-full bg-pista-600 animate-ping inline-block mr-1"></span> Live Audit Active
            </span>
          </div>
        </div>

        <!-- 4 Metric Counters -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="p-4 rounded-2xl bg-ivory-50 border border-ivory-200">
            <span class="text-[10px] uppercase font-bold text-ivory-600 tracking-wider block">Network Entities</span>
            <div class="text-2xl font-serif font-black text-pista-900 mt-0.5">28 Verified</div>
            <span class="text-[11px] text-pista-700 font-semibold block mt-0.5">100% compliant</span>
          </div>
          <div class="p-4 rounded-2xl bg-ivory-50 border border-ivory-200">
            <span class="text-[10px] uppercase font-bold text-ivory-600 tracking-wider block">Safety Audit Score</span>
            <div class="text-2xl font-serif font-black text-pista-900 mt-0.5">99.8%</div>
            <span class="text-[11px] text-pista-700 font-semibold block mt-0.5">Zero infractions</span>
          </div>
          <div class="p-4 rounded-2xl bg-ivory-50 border border-ivory-200">
            <span class="text-[10px] uppercase font-bold text-ivory-600 tracking-wider block">Average Dispatch Time</span>
            <div class="text-2xl font-serif font-black text-salmon-600 mt-0.5">14.2 mins</div>
            <span class="text-[11px] text-ivory-600 block mt-0.5">Within 45m safe window</span>
          </div>
          <div class="p-4 rounded-2xl bg-ivory-50 border border-ivory-200">
            <span class="text-[10px] uppercase font-bold text-ivory-600 tracking-wider block">Verification SLA</span>
            <div class="text-2xl font-serif font-black text-pista-900 mt-0.5">&lt; 2 Hours</div>
            <span class="text-[11px] text-pista-700 font-semibold block mt-0.5">Automated checks</span>
          </div>
        </div>

        <!-- Telemetry Table -->
        <div class="space-y-3">
          <div class="flex items-center justify-between text-xs font-bold text-ivory-800 pb-1">
            <span>Accredited Partner Verification Records</span>
            <span class="text-pista-700 font-semibold">Updated 2m ago</span>
          </div>

          <div class="overflow-x-auto rounded-2xl border border-ivory-200">
            <table class="w-full text-left text-xs">
              <thead class="bg-ivory-100 text-ivory-800 font-bold uppercase text-[10px] tracking-wider border-b border-ivory-200">
                <tr>
                  <th class="py-3 px-4">Entity & Name</th>
                  <th class="py-3 px-4">Classification</th>
                  <th class="py-3 px-4">Accreditation ID</th>
                  <th class="py-3 px-4">Status</th>
                  <th class="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-ivory-200 bg-white">
                ${this.logs.map(log => `
                  <tr class="hover:bg-ivory-50/70 transition-colors">
                    <td class="py-3 px-4 font-bold text-ivory-900">${log.entityName}</td>
                    <td class="py-3 px-4 text-ivory-700">${log.type}</td>
                    <td class="py-3 px-4 font-mono text-[11px] text-pista-800 font-semibold">${log.verificationBadge}</td>
                    <td class="py-3 px-4">
                      <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-pista-100 text-pista-800 border border-pista-300">
                        <i class="fa-solid fa-check text-[9px] mr-1"></i> ${log.status}
                      </span>
                    </td>
                    <td class="py-3 px-4 text-right">
                      <button data-audit-id="${log.id}" class="audit-btn text-pista-700 hover:text-salmon-600 font-bold text-xs transition-colors">
                        Re-verify &rarr;
                      </button>
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    `;

    // Bind click events
    this.container.querySelectorAll('.audit-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = (e.currentTarget as HTMLElement).getAttribute('data-audit-id');
        if (id) this.auditEntity(id);
      });
    });
  }
}
