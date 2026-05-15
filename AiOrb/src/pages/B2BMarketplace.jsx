import { Key, Database, Globe, ArrowRight } from 'lucide-react';
import TopBar from '../components/TopBar';
import Card from '../components/GlowCard';

export default function B2BMarketplace() {
  return (
    <div className="p-8 w-full max-w-[1600px] mx-auto relative">
      <TopBar title="B2B Data Licensing" subtitle="Provide AiOrb's friction and threat intelligence data to partner applications" />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
        {[
          { label: 'Active API Consumers', value: '1,420', sub: 'Partner apps using our data', icon: Globe },
          { label: 'Total API Calls', value: '14.2M', sub: 'Last 30 days', icon: Database },
          { label: 'Licensed Models', value: '3', sub: 'Fraud, UX, Accessibility', icon: Key },
        ].map((s, i) => {
          const Icon = s.icon;
          return (
            <div key={i} className="panel p-8">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 rounded-full bg-[rgba(246,168,33,0.1)] text-[#f6a821] flex items-center justify-center">
                  <Icon className="w-6 h-6" />
                </div>
                <p className="text-[14px] text-[#c0cdd8] font-light">{s.label}</p>
              </div>
              <p className="stat-num text-[38px] text-white mb-2 leading-none">{s.value}</p>
              <p className="text-[13px] text-[#8fa5b8] font-light">{s.sub}</p>
            </div>
          );
        })}
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        
        {/* Data Models Available */}
        <Card delay={1} className="overflow-hidden flex flex-col">
          <div className="px-8 py-6 border-b border-[#3f5063] flex flex-shrink-0 flex-col">
            <h3 className="text-[18px] font-light text-white">Available Data Streams</h3>
            <p className="text-[13px] text-[#c0cdd8] mt-1 font-light">Data packages available for B2B integration</p>
          </div>
          <div className="flex-1 overflow-auto p-8 space-y-4">
            {[
              { name: 'UX Friction Intel', desc: 'Real-time stats on where users hesitate and struggle in specific app categories.', price: 'Enterprise' },
              { name: 'Threat & Fraud Signatures', desc: 'Live feed of malicious patterns, scam URLs, and behavioral anomalies.', price: 'Standard' },
              { name: 'Accessibility Profiles', desc: 'Data on UI interventions needed for visually or cognitively impaired users.', price: 'Premium' }
            ].map((stream, i) => (
              <div key={i} className="bg-[#202b38] border border-[#3f5063] rounded-xl p-6 hover:border-[#f6a821] trans">
                <div className="flex justify-between items-center mb-2">
                  <h4 className="text-[15px] font-medium text-white">{stream.name}</h4>
                  <span className="badge badge-yellow">{stream.price}</span>
                </div>
                <p className="text-[13px] text-[#8fa5b8] mb-4">{stream.desc}</p>
                <button className="text-[12px] font-medium text-[#f6a821] hover:text-[#e59b1d] flex items-center gap-1 uppercase tracking-wider trans">
                  Generate API Key <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        </Card>

        {/* API Integration Docs */}
        <Card delay={2} className="overflow-hidden flex flex-col">
          <div className="px-8 py-6 border-b border-[#3f5063] flex flex-shrink-0 flex-col">
            <h3 className="text-[18px] font-light text-white">Integration Sandbox</h3>
            <p className="text-[13px] text-[#c0cdd8] mt-1 font-light">How partner apps consume our intelligence</p>
          </div>
          <div className="p-8">
            <div className="bg-[#151e28] rounded-lg border border-[#3f5063] p-5 mb-6">
              <p className="text-[12px] text-[#8fa5b8] font-mono mb-2">// Fetching UX Friction data for your app</p>
              <pre className="text-[13px] text-[#21b978] font-mono">
{`fetch('https://api.aiorb.com/v1/friction', {
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY'
  }
})
.then(res => res.json())
.then(data => analyzeFriction(data));`}
              </pre>
            </div>
            <div className="space-y-4">
              <h4 className="text-[14px] text-white font-medium mb-2">Why integrate AiOrb Data?</h4>
              <ul className="text-[13px] text-[#c0cdd8] space-y-2 list-disc pl-4">
                <li>Proactively identify UI elements causing users to abandon tasks.</li>
                <li>Block fraudulent transactions by cross-referencing our live scam registry.</li>
                <li>Automatically adjust your app's UI based on global accessibility metrics.</li>
              </ul>
            </div>
          </div>
        </Card>

      </div>
    </div>
  );
}
