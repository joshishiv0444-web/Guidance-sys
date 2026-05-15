import { useState, useEffect } from 'react';
import { Activity, CheckCircle2, AlertTriangle, Zap } from 'lucide-react';
import TopBar from '../components/TopBar';
import Card from '../components/GlowCard';

export default function AppComplexity() {
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:5000/api/friction')
      .then(res => res.json())
      .then(data => {
        // Mock processing the friction data into easy/complex
        // If hesitation < 10 and oscillation < 40 -> Easy
        const processed = data.map(app => {
          const isEasy = app.avgHesitation < 10 && app.oscillationRate < 40;
          return {
            ...app,
            complexity: isEasy ? 'Easy to Use' : 'Complex',
            aiInterventions: isEasy ? Math.floor(Math.random() * 5) : Math.floor(Math.random() * 50) + 15,
            completionTime: isEasy ? 'Fast' : 'Slow',
          };
        });
        setApps(processed);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const easyApps = apps.filter(a => a.complexity === 'Easy to Use');
  const complexApps = apps.filter(a => a.complexity === 'Complex');

  return (
    <div className="p-8 w-full max-w-[1600px] mx-auto relative">
      <TopBar title="App Complexity Analysis" subtitle="AI-driven insights on user friction and ease of use across integrated apps" />

      {loading ? (
        <div className="text-[#8fa5b8] text-center mt-8">Loading app metrics...</div>
      ) : (
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Easy Apps */}
          <Card delay={1} className="overflow-hidden flex flex-col h-[500px]">
            <div className="px-8 py-6 border-b border-[#3f5063] flex justify-between items-center bg-[rgba(33,185,120,0.05)]">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-[#21b978]" />
                <h3 className="text-[18px] font-light text-white">Frictionless Apps</h3>
              </div>
              <span className="badge badge-green">{easyApps.length} Apps</span>
            </div>
            <div className="flex-1 overflow-auto p-4 space-y-3">
              {easyApps.length === 0 ? (
                <p className="text-[13px] text-[#8fa5b8] text-center mt-4">No highly optimized apps found yet.</p>
              ) : (
                easyApps.map((app, i) => (
                  <div key={i} className="p-5 border border-[#3f5063] rounded bg-[#202b38] flex justify-between items-center hover:bg-[#253342] trans">
                    <div>
                      <p className="text-[14px] font-medium text-white mb-1">{app.app} <span className="text-[11px] text-[#8fa5b8]">({app.screen})</span></p>
                      <div className="flex items-center gap-3 text-[12px] text-[#8fa5b8]">
                        <span className="flex items-center gap-1"><Zap className="w-3 h-3 text-[#f6a821]" /> Fast Completion</span>
                        <span>•</span>
                        <span>{app.aiInterventions} AI Prompts/User</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-[13px] font-medium text-[#21b978]">Smooth</p>
                      <p className="text-[11px] text-[#8fa5b8]">{app.avgHesitation}s avg wait</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>

          {/* Complex Apps */}
          <Card delay={2} className="overflow-hidden flex flex-col h-[500px]">
            <div className="px-8 py-6 border-b border-[#3f5063] flex justify-between items-center bg-[rgba(234,88,12,0.05)]">
              <div className="flex items-center gap-3">
                <AlertTriangle className="w-5 h-5 text-[#ea580c]" />
                <h3 className="text-[18px] font-light text-white">Complex Apps (High Friction)</h3>
              </div>
              <span className="badge badge-red">{complexApps.length} Apps</span>
            </div>
            <div className="flex-1 overflow-auto p-4 space-y-3">
              {complexApps.length === 0 ? (
                <p className="text-[13px] text-[#8fa5b8] text-center mt-4">No complex apps found.</p>
              ) : (
                complexApps.map((app, i) => (
                  <div key={i} className="p-5 border border-[#3f5063] rounded bg-[#202b38] flex justify-between items-center hover:bg-[#253342] trans">
                    <div>
                      <p className="text-[14px] font-medium text-white mb-1">{app.app} <span className="text-[11px] text-[#8fa5b8]">({app.screen})</span></p>
                      <div className="flex items-center gap-3 text-[12px] text-[#8fa5b8]">
                        <span className="flex items-center gap-1"><Activity className="w-3 h-3 text-[#ea580c]" /> High Drop-off Risk</span>
                        <span>•</span>
                        <span>{app.aiInterventions} AI Prompts/User</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-[13px] font-medium text-[#ea580c]">Heavy Friction</p>
                      <p className="text-[11px] text-[#8fa5b8]">{app.avgHesitation}s avg wait</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
