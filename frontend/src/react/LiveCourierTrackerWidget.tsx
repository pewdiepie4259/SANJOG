import React, { useState } from 'react';

export const LiveCourierTrackerWidget: React.FC = () => {
  const [donorOtp, setDonorOtp] = useState<string>('');
  const [receiverOtp, setReceiverOtp] = useState<string>('');
  const [pickupVerified, setPickupVerified] = useState<boolean>(false);
  const [deliveryVerified, setDeliveryVerified] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string>('');

  const handleVerifyChef = () => {
    if (donorOtp.trim() === '7492') {
      setPickupVerified(true);
      setErrorMsg('');
      const win = window as any;
      if (typeof win.showToast === 'function') {
        win.showToast('Kitchen pickup confirmed with Chef Rajesh OTP 7492!');
      }
    } else {
      setErrorMsg('Invalid Chef OTP. Try demo code 7492.');
    }
  };

  const handleVerifyShelter = () => {
    if (receiverOtp.trim() === '3180') {
      setDeliveryVerified(true);
      setErrorMsg('');
      const win = window as any;
      if (typeof win.showToast === 'function') {
        win.showToast('Shelter handover confirmed with Sister Maria OTP 3180!');
      }
    } else {
      setErrorMsg('Invalid Shelter OTP. Try demo code 3180.');
    }
  };

  const isCompleted = pickupVerified && deliveryVerified;

  return (
    <div className="bg-white p-6 sm:p-8 rounded-3xl border border-ivory-300 shadow-soft max-w-4xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-ivory-200 gap-3">
        <div>
          <span className="px-3 py-1 bg-pista-100 text-pista-900 border border-pista-300 rounded-full text-xs font-bold inline-flex items-center gap-1.5 mb-2">
            <i className="fa-solid fa-atom text-pista-700"></i>
            <span>React Real-Time Dispatch Engine</span>
          </span>
          <h2 className="font-serif text-2xl font-black text-pista-950">Active Rescue Dispatch #RS-941</h2>
          <p className="text-xs text-ivory-700 mt-1">Dual-PIN cryptographic food custody verification in transit.</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 rounded-xl bg-pista-100 text-pista-800 font-bold text-xs border border-pista-300 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-pista-600 animate-ping"></span>
            <span>{isCompleted ? 'Mission Completed' : pickupVerified ? 'In Transit • 8m ETA' : 'En Route to Kitchen'}</span>
          </span>
        </div>
      </div>

      {/* Completion Banner */}
      {isCompleted && (
        <div className="p-5 rounded-2xl bg-pista-100 border border-pista-400 text-pista-900 shadow-pista flex items-center gap-4 animate-fadeIn">
          <div className="w-12 h-12 rounded-xl bg-pista-700 text-ivory-50 flex items-center justify-center text-xl shrink-0">
            <i className="fa-solid fa-circle-check"></i>
          </div>
          <div>
            <h4 className="font-serif text-base font-bold text-pista-950">
              Food Rescue Mission #RS-941 Successfully Completed!
            </h4>
            <p className="text-xs text-pista-800 mt-0.5">
              60 fresh meals were safely transported from Annapurna Grand and received at Hope Community Shelter. FSSAI hygiene chain verified.
            </p>
          </div>
        </div>
      )}

      {errorMsg && (
        <div className="p-3 bg-salmon-50 border border-salmon-300 text-salmon-700 rounded-xl text-xs font-bold flex items-center gap-2">
          <i className="fa-solid fa-triangle-exclamation"></i>
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Courier & Vehicle Card */}
      <div className="bg-ivory-50 p-5 rounded-2xl border border-ivory-300 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-pista-200 text-pista-800 flex items-center justify-center text-lg font-bold">
            <i className="fa-solid fa-person-biking"></i>
          </div>
          <div>
            <span className="text-[10px] uppercase font-bold text-ivory-600 tracking-wider">Assigned Volunteer Courier</span>
            <div className="text-sm font-bold text-ivory-900 mt-0.5">Aniket Kumar • Rating: 4.9 ★</div>
            <span className="text-xs text-ivory-600">TVS iQube EV (KA-03-HA-8192) • Insulated Thermal Catering Box</span>
          </div>
        </div>

        <div className="flex items-center gap-3 text-xs border-t md:border-t-0 md:border-l border-ivory-200 pt-3 md:pt-0 md:pl-5">
          <div>
            <span className="text-ivory-600 block text-[11px]">Distance</span>
            <span className="font-bold text-pista-900">3.8 km</span>
          </div>
          <span className="text-ivory-300">•</span>
          <div>
            <span className="text-ivory-600 block text-[11px]">Temp at Pickup</span>
            <span className="font-bold text-pista-900">68°C (Hot)</span>
          </div>
          <span className="text-ivory-300">•</span>
          <div>
            <span className="text-ivory-600 block text-[11px]">CO₂ Avoided</span>
            <span className="font-bold text-salmon-600">3.8 kg</span>
          </div>
        </div>
      </div>

      {/* 2-Step OTP Validation Console */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Step 1: Donor Kitchen PIN */}
        <div className="p-5 rounded-2xl border border-ivory-300 bg-white space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-pista-800 flex items-center gap-1.5">
              <i className="fa-solid fa-utensils text-pista-600"></i> Step 1: Kitchen Pickup Handover
            </span>
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
              pickupVerified ? 'bg-pista-100 text-pista-800' : 'bg-salmon-100 text-salmon-700'
            }`}>
              {pickupVerified ? 'Verified' : 'Pending OTP'}
            </span>
          </div>
          <p className="text-xs text-ivory-600 leading-normal">
            Chef Rajesh at Annapurna Grand holds the 4-digit verification PIN to confirm food departure.
          </p>

          <div className="p-3 bg-ivory-100/70 rounded-xl space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-ivory-700">Chef PIN:</span>
              <span className="font-mono font-bold text-pista-800 bg-white px-2 py-0.5 rounded border border-ivory-200">
                7492
              </span>
            </div>
            {!pickupVerified ? (
              <div className="flex gap-2">
                <input
                  type="text"
                  maxLength={4}
                  placeholder="Enter 7492"
                  value={donorOtp}
                  onChange={e => setDonorOtp(e.target.value)}
                  className="w-full px-3 py-1.5 text-xs border border-ivory-300 rounded-lg text-center font-mono font-bold tracking-widest focus:ring-2 focus:ring-pista-400"
                />
                <button
                  onClick={handleVerifyChef}
                  className="px-4 py-1.5 bg-pista-700 hover:bg-pista-800 text-ivory-50 text-xs font-bold rounded-lg shadow-xs transition-colors shrink-0"
                >
                  Confirm
                </button>
              </div>
            ) : (
              <div className="text-xs font-bold text-pista-700 flex items-center gap-1.5 py-1">
                <i className="fa-solid fa-check"></i> Food Custody Transferred to Courier
              </div>
            )}
          </div>
        </div>

        {/* Step 2: Shelter Handover PIN */}
        <div className="p-5 rounded-2xl border border-ivory-300 bg-white space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-salmon-700 flex items-center gap-1.5">
              <i className="fa-solid fa-people-roof text-salmon-500"></i> Step 2: Shelter Delivery Handover
            </span>
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
              deliveryVerified ? 'bg-pista-100 text-pista-800' : 'bg-ivory-200 text-ivory-700'
            }`}>
              {deliveryVerified ? 'Verified' : 'On Arrival'}
            </span>
          </div>
          <p className="text-xs text-ivory-600 leading-normal">
            Sister Maria at Hope Community Shelter verifies meal temperature and packaging on delivery.
          </p>

          <div className="p-3 bg-ivory-100/70 rounded-xl space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-ivory-700">Shelter PIN:</span>
              <span className="font-mono font-bold text-salmon-700 bg-white px-2 py-0.5 rounded border border-ivory-200">
                3180
              </span>
            </div>
            {!deliveryVerified ? (
              <div className="flex gap-2">
                <input
                  type="text"
                  maxLength={4}
                  placeholder="Enter 3180"
                  value={receiverOtp}
                  onChange={e => setReceiverOtp(e.target.value)}
                  className="w-full px-3 py-1.5 text-xs border border-ivory-300 rounded-lg text-center font-mono font-bold tracking-widest focus:ring-2 focus:ring-salmon-400"
                />
                <button
                  onClick={handleVerifyShelter}
                  className="px-4 py-1.5 bg-salmon-500 hover:bg-salmon-600 text-white text-xs font-bold rounded-lg shadow-salmon transition-colors shrink-0"
                >
                  Confirm
                </button>
              </div>
            ) : (
              <div className="text-xs font-bold text-pista-700 flex items-center gap-1.5 py-1">
                <i className="fa-solid fa-check"></i> Shelter Handover Confirmed & Signed
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
