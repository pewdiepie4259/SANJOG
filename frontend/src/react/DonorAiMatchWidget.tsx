import React, { useState } from 'react';
import { SurplusBatch, MealDemand } from '../types';

interface DonorAiMatchWidgetProps {
  initialListing?: SurplusBatch;
}

export const DonorAiMatchWidget: React.FC<DonorAiMatchWidgetProps> = () => {
  const [selectedUrgency, setSelectedUrgency] = useState<string>('ALL');
  const [servingsFilter, setServingsFilter] = useState<number>(60);
  const [matched, setMatched] = useState<boolean>(false);

  const candidateShelters: MealDemand[] = [
    {
      id: 'DMD-802',
      receiverName: 'Hope Community Shelter & Kitchen',
      mealsNeeded: 80,
      beneficiaries: 'Homeless families & children (St. Marks Road)',
      dietaryPreference: 'Any Nutritious Food',
      targetTime: 'Tonight before 9:00 PM',
      urgency: 'HIGH',
      storage: 'Refrigeration Available',
      darpanVerified: true,
      location: '3.8 km away • 12 mins via Indiranagar Link'
    },
    {
      id: 'DMD-803',
      receiverName: 'Ashraya Orphanage Trust',
      mealsNeeded: 35,
      beneficiaries: 'School Children (Wilson Garden)',
      dietaryPreference: 'Strict Vegetarian',
      targetTime: 'Immediate Dinner Serving',
      urgency: 'CRITICAL',
      storage: 'Immediate Serving',
      darpanVerified: true,
      location: '5.1 km away • 16 mins'
    },
    {
      id: 'DMD-804',
      receiverName: 'Karuna Senior Care Home',
      mealsNeeded: 45,
      beneficiaries: 'Elderly Residents (Shivajinagar)',
      dietaryPreference: 'Low Spice / Soft Meals',
      targetTime: 'Tonight 8:30 PM',
      urgency: 'MODERATE',
      storage: 'Hot Food Warmers',
      darpanVerified: true,
      location: '4.4 km away • 14 mins'
    }
  ];

  const filteredShelters = candidateShelters.filter(s => {
    if (selectedUrgency !== 'ALL' && s.urgency !== selectedUrgency) return false;
    return true;
  });

  const handlePairing = (shelter: MealDemand) => {
    setMatched(true);
    const win = window as any;
    if (typeof win.showToast === 'function') {
      win.showToast(`AI Match Confirmed! Paired with ${shelter.receiverName}. Courier Aniket dispatched.`);
    }
    setTimeout(() => {
      if (typeof win.showView === 'function') {
        win.showView('donor-tracking');
      }
    }, 900);
  };

  return (
    <div className="bg-white p-6 rounded-3xl border border-ivory-300 shadow-soft space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-ivory-200">
        <div>
          <span className="px-3 py-1 bg-pista-100 text-pista-800 border border-pista-300 rounded-full text-xs font-bold inline-flex items-center gap-1.5 mb-2">
            <i className="fa-solid fa-microchip text-pista-700"></i>
            <span>React AI Pairing Engine</span>
          </span>
          <h2 className="font-serif text-2xl font-black text-pista-950">Intelligent Food Rescue Matcher</h2>
          <p className="text-xs text-ivory-700 mt-1">
            Real-time geospatial pairing evaluating kitchen shelf-life, shelter demand, and courier proximity.
          </p>
        </div>

        {/* Quick Filter Bar */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-ivory-700 font-bold hidden md:inline">Urgency:</span>
          {(['ALL', 'CRITICAL', 'HIGH'] as const).map(u => (
            <button
              key={u}
              onClick={() => setSelectedUrgency(u)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                selectedUrgency === u
                  ? 'bg-pista-700 text-ivory-50 shadow-xs'
                  : 'bg-ivory-100 text-ivory-800 hover:bg-pista-100 border border-ivory-300'
              }`}
            >
              {u === 'ALL' ? 'All Demands' : u}
            </button>
          ))}
        </div>
      </div>

      {/* Interactive Controls & Match Spotlight */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 rounded-2xl bg-pista-50/70 border border-pista-200">
        <div className="space-y-1">
          <span className="text-[10px] font-bold uppercase tracking-wider text-pista-800">Donor Surplus Batch</span>
          <div className="text-sm font-bold text-pista-950">60 Thalis • Annapurna Grand</div>
          <span className="text-xs text-ivory-600 block">Indiranagar • Cooked 40m ago (68°C)</span>
        </div>

        <div className="space-y-1.5">
          <div className="flex justify-between text-xs font-bold text-pista-900">
            <span>Servings Ready:</span>
            <span>{servingsFilter} Meals</span>
          </div>
          <input
            type="range"
            min={20}
            max={150}
            value={servingsFilter}
            onChange={e => setServingsFilter(Number(e.target.value))}
            className="w-full accent-pista-700 cursor-pointer h-1.5 bg-ivory-200 rounded-lg"
          />
          <span className="text-[10px] text-ivory-600 block">Dynamically recalculated in real-time</span>
        </div>

        <div className="flex flex-col justify-center space-y-1 bg-white p-3 rounded-xl border border-pista-300">
          <div className="flex items-center justify-between text-xs">
            <span className="text-ivory-700 font-semibold">Match Confidence:</span>
            <span className="font-bold text-pista-700">98.4% Optimal</span>
          </div>
          <div className="w-full bg-ivory-200 h-2 rounded-full overflow-hidden">
            <div className="bg-pista-600 h-2 rounded-full transition-all" style={{ width: '98.4%' }}></div>
          </div>
          <span className="text-[10px] text-salmon-600 font-bold">Estimated Handover: 22 mins</span>
        </div>
      </div>

      {/* Candidate Shelter Cards */}
      <div className="space-y-3">
        <div className="flex items-center justify-between text-xs font-bold text-ivory-800 pb-1">
          <span>Top Matched Community Care Centers ({filteredShelters.length})</span>
          <span className="text-pista-700 font-semibold flex items-center gap-1">
            <i className="fa-solid fa-circle-check text-pista-600"></i> Verified DARPAN NGOs
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {filteredShelters.map((shelter, idx) => (
            <div
              key={shelter.id}
              className={`p-5 rounded-2xl border transition-all flex flex-col justify-between gap-4 group ${
                idx === 0
                  ? 'bg-pista-50/50 border-pista-400 ring-2 ring-pista-300/40 shadow-soft'
                  : 'bg-white border-ivory-300 hover:border-salmon-300'
              }`}
            >
              <div className="space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <span className="text-xs font-bold text-pista-900 group-hover:text-salmon-600 transition-colors">
                    {shelter.receiverName}
                  </span>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                      shelter.urgency === 'CRITICAL'
                        ? 'bg-salmon-100 text-salmon-700 border border-salmon-300'
                        : 'bg-pista-100 text-pista-800 border border-pista-300'
                    }`}
                  >
                    {shelter.urgency}
                  </span>
                </div>

                <div className="text-sm font-black text-pista-950 flex items-center gap-1">
                  <i className="fa-solid fa-bowl-food text-salmon-500 text-xs"></i>
                  <span>{shelter.mealsNeeded} Meals Needed</span>
                </div>

                <p className="text-xs text-ivory-700 line-clamp-2 leading-relaxed">
                  {shelter.beneficiaries}
                </p>

                <div className="p-2.5 bg-ivory-100/70 rounded-xl text-[11px] text-ivory-700 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-ivory-600">Proximity:</span>
                    <span className="font-bold text-ivory-900">{shelter.location}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-ivory-600">Serving Window:</span>
                    <span className="font-semibold text-salmon-600">{shelter.targetTime}</span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => handlePairing(shelter)}
                disabled={matched}
                className="w-full py-2.5 px-3 bg-pista-700 hover:bg-pista-800 text-ivory-50 text-xs font-bold rounded-xl transition-all shadow-pista flex items-center justify-center gap-2 group-hover:scale-[1.01]"
              >
                <i className="fa-solid fa-handshake-angle text-xs"></i>
                <span>{matched ? 'Match Dispatched!' : 'Confirm Match & Courier'}</span>
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
