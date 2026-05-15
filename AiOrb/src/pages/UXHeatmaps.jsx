import { useState, useEffect } from 'react';
import TopBar from '../components/TopBar';
import Card from '../components/GlowCard';

export default function UXHeatmaps() {
  const [frictionData, setFrictionData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:5000/api/friction')
      .then(res => res.json())
      .then(data => {
        setFrictionData(data || []);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="p-8 w-full max-w-[1600px] mx-auto relative">
      <TopBar title="UX Friction & Heatmaps" subtitle="Analyze user hesitation points and app struggles" />

      {loading ? (
        <div className="text-[#8fa5b8] text-center mt-8">Loading data...</div>
      ) : frictionData.length === 0 ? (
        <div className="text-[#8fa5b8] text-center mt-8">No friction data available from the backend yet. Provide MongoDB database later.</div>
      ) : (
        <Card delay={1} className="overflow-hidden flex flex-col">
          <div className="px-8 py-6 border-b border-[#3f5063] flex flex-shrink-0 flex-col">
            <h3 className="text-[18px] font-light text-white">Friction Points (App specific)</h3>
            <p className="text-[13px] text-[#c0cdd8] mt-1 font-light">Where users get stuck across applications</p>
          </div>
          <div className="p-8 grid md:grid-cols-3 gap-8">
            {frictionData.map((data, i) => (
              <div key={i} className="p-6 border border-[#3f5063] rounded bg-[#202b38] hover:border-[#f6a821] trans">
                <p className="text-[12px] text-[#f6a821] font-medium uppercase tracking-wider mb-1">{data.app}</p>
                <p className="text-[16px] text-white font-light mb-6">{data.screen}</p>
                
                <div className="flex justify-between items-end mb-2">
                  <span className="text-[12px] font-light text-[#8fa5b8]">Avg Hesitation</span>
                  <span className="text-[14px] text-white font-light">{data.avgHesitation}s</span>
                </div>
                <div className="h-1.5 w-full bg-[#314256] rounded-full overflow-hidden mb-5">
                  <div className="h-full bg-[#f6a821] rounded-full" style={{ width: `${(data.avgHesitation / 20) * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
