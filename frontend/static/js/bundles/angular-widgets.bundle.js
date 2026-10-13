"use strict";(()=>{var d=Object.defineProperty;var l=(e,t,i)=>t in e?d(e,t,{enumerable:!0,configurable:!0,writable:!0,value:i}):e[t]=i;var a=(e,t,i)=>l(e,typeof t!="symbol"?t+"":t,i);var r=class{constructor(t){a(this,"container");a(this,"logs",[{id:"AUD-901",entityName:"Annapurna Grand (Indiranagar)",type:"Commercial Kitchen",verificationBadge:"FSSAI #11221334000192",status:"APPROVED",timestamp:"15 mins ago"},{id:"AUD-902",entityName:"Hope Community Shelter (St. Marks)",type:"Shelter Home",verificationBadge:"DARPAN #KA/2021/0298412",status:"APPROVED",timestamp:"42 mins ago"},{id:"AUD-903",entityName:"GreenLeaf Organic Cafe (MG Road)",type:"Bakery & Fresh Produce",verificationBadge:"FSSAI #11222334000455",status:"APPROVED",timestamp:"1h 10m ago"},{id:"AUD-904",entityName:"Karuna Senior Care Home (Shivajinagar)",type:"Elderly Care",verificationBadge:"DARPAN #KA/2020/0187291",status:"APPROVED",timestamp:"2h ago"}]);this.container=t,this.render()}auditEntity(t){let i=this.logs.find(s=>s.id===t);if(i){let s=window;typeof s.showToast=="function"&&s.showToast(`Auditing ${i.entityName}... FSSAI / DARPAN record re-verified!`)}this.render()}render(){this.container.innerHTML=`
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
                ${this.logs.map(t=>`
                  <tr class="hover:bg-ivory-50/70 transition-colors">
                    <td class="py-3 px-4 font-bold text-ivory-900">${t.entityName}</td>
                    <td class="py-3 px-4 text-ivory-700">${t.type}</td>
                    <td class="py-3 px-4 font-mono text-[11px] text-pista-800 font-semibold">${t.verificationBadge}</td>
                    <td class="py-3 px-4">
                      <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-pista-100 text-pista-800 border border-pista-300">
                        <i class="fa-solid fa-check text-[9px] mr-1"></i> ${t.status}
                      </span>
                    </td>
                    <td class="py-3 px-4 text-right">
                      <button data-audit-id="${t.id}" class="audit-btn text-pista-700 hover:text-salmon-600 font-bold text-xs transition-colors">
                        Re-verify &rarr;
                      </button>
                    </td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    `,this.container.querySelectorAll(".audit-btn").forEach(t=>{t.addEventListener("click",i=>{let s=i.currentTarget.getAttribute("data-audit-id");s&&this.auditEntity(s)})})}};var o=class{constructor(t){a(this,"container");a(this,"verified",!0);this.container=t,this.render()}verifyChain(){let t=window;typeof t.showToast=="function"&&t.showToast("Blockchain & FSSAI Digital Provenance Chain: Verified Authentic (SHA-256 Valid)!"),this.render()}render(){this.container.innerHTML=`
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
            <p class="text-[11px] text-ivory-700">FSSAI #11221334000192 \u2022 Indiranagar</p>
            <div class="pt-2 border-t border-pista-200 text-[10px] text-pista-800 font-semibold">
              Cooked at 68\xB0C \u2022 Sealed Thermal Trays
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
              Insulated Bain-marie \u2022 Transit: 12 mins
            </div>
          </div>

          <div class="p-4 rounded-2xl bg-salmon-50 border border-salmon-200 space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-bold uppercase tracking-wider text-salmon-800">3. Verified Shelter</span>
              <i class="fa-solid fa-hands-holding-child text-salmon-600 text-xs"></i>
            </div>
            <div class="text-sm font-bold text-salmon-950">Hope Community Shelter</div>
            <p class="text-[11px] text-ivory-700">DARPAN #KA/2021/0298412 \u2022 St. Marks</p>
            <div class="pt-2 border-t border-salmon-200 text-[10px] text-salmon-800 font-semibold">
              Temperature on Handover: 62\xB0C (Safe)
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
    `;let t=this.container.querySelector("#verify-passport-btn");t&&t.addEventListener("click",()=>this.verifyChain())}};function n(){let e=document.getElementById("angular-telemetry-root");e&&new r(e);let t=document.getElementById("angular-passport-root");t&&new o(t)}typeof window<"u"&&(document.readyState==="loading"?document.addEventListener("DOMContentLoaded",n):n());})();
