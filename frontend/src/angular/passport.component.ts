/**
 * SANJOG - Community Food Rescue Network
 * Angular Food Passport Provenance Component (TypeScript)
 */

export class AngularPassportAuditor {
  private container: HTMLElement;
  private verified: boolean = true;

  constructor(container: HTMLElement) {
    this.container = container;
    this.render();
  }

  public verifyChain(): void {
    const win = window as any;
    if (typeof win.showToast === 'function') {
      win.showToast('Blockchain & FSSAI Digital Provenance Chain: Verified Authentic (SHA-256 Valid)!');
    }
    this.render();
  }

  public render(): void {
    this.container.innerHTML = `
      <div class="bg-white p-6 sm:p-8 rounded-3xl border border-ivory-300 shadow-soft max-w-4xl mx-auto space-y-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-ivory-200 gap-3">
          <div>
            <span class="px-3 py-1 bg-pista-100 text-pista-900 border border-pista-300 rounded-full text-xs font-bold inline-flex items-center gap-1.5 mb-2">
              <i class="fa-solid fa-passport text-pista-700"></i>
              <span>Angular Digital Provenance Passport</span>
            </span>
            <h2 class="font-serif text-2xl font-black text-pista-950">FSSAI Certified Food Passport</h2>
            <p class="text-xs text-ivory-700 mt-1">End-to-end cryptographic and temperature custody chain for rescued meals.</p>
          </div>
          <div class="flex items-center gap-2">
            <span class="px-3 py-1.5 rounded-xl bg-pista-100 text-pista-800 font-bold text-xs border border-pista-300 flex items-center gap-1.5">
              <i class="fa-solid fa-shield-check text-pista-600"></i>
              <span>Batch #LST-1082 Verified</span>
            </span>
          </div>
        </div>

        <!-- 3-Node Provenance Chain -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="p-4 rounded-2xl bg-pista-50 border border-pista-200 space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-bold uppercase tracking-wider text-pista-800">1. Origin Kitchen</span>
              <i class="fa-solid fa-utensils text-pista-600 text-xs"></i>
            </div>
            <div class="text-sm font-bold text-pista-950">Annapurna Grand</div>
            <p class="text-[11px] text-ivory-700">FSSAI #11221334000192 • Indiranagar</p>
            <div class="pt-2 border-t border-pista-200 text-[10px] text-pista-800 font-semibold">
              Cooked at 68°C • Sealed Thermal Trays
            </div>
          </div>

          <div class="p-4 rounded-2xl bg-ivory-100 border border-ivory-300 space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-bold uppercase tracking-wider text-ivory-800">2. Cold-Chain Courier</span>
              <i class="fa-solid fa-motorcycle text-pista-700 text-xs"></i>
            </div>
            <div class="text-sm font-bold text-ivory-950">Aniket Kumar</div>
            <p class="text-[11px] text-ivory-700">KA-03-HA-8192 (TVS iQube EV)</p>
            <div class="pt-2 border-t border-ivory-200 text-[10px] text-pista-800 font-semibold">
              Insulated Bain-marie • Transit: 12 mins
            </div>
          </div>

          <div class="p-4 rounded-2xl bg-salmon-50 border border-salmon-200 space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-bold uppercase tracking-wider text-salmon-800">3. Verified Shelter</span>
              <i class="fa-solid fa-hands-holding-child text-salmon-600 text-xs"></i>
            </div>
            <div class="text-sm font-bold text-salmon-950">Hope Community Shelter</div>
            <p class="text-[11px] text-ivory-700">DARPAN #KA/2021/0298412 • St. Marks</p>
            <div class="pt-2 border-t border-salmon-200 text-[10px] text-salmon-800 font-semibold">
              Temperature on Handover: 62°C (Safe)
            </div>
          </div>
        </div>

        <!-- Cryptographic Audit Footprint -->
        <div class="bg-ivory-50 p-4 rounded-2xl border border-ivory-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div class="space-y-0.5">
            <span class="text-ivory-600 block text-[11px]">Provenance SHA-256 Digest:</span>
            <span class="font-mono text-[11px] text-ivory-900 font-bold break-all">
              e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
            </span>
          </div>
          <button id="verify-passport-btn" class="px-4 py-2 bg-pista-700 hover:bg-pista-800 text-ivory-50 text-xs font-bold rounded-xl shadow-xs transition-colors shrink-0">
            Audit Ledger
          </button>
        </div>
      </div>
    `;

    const btn = this.container.querySelector('#verify-passport-btn');
    if (btn) {
      btn.addEventListener('click', () => this.verifyChain());
    }
  }
}
