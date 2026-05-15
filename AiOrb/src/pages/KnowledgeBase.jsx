import { useState } from 'react';
import { Database, Plus, CheckCircle2, AlertTriangle, Loader2 } from 'lucide-react';
import TopBar from '../components/TopBar';
import Card from '../components/GlowCard';

export default function KnowledgeBase() {
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null); // { type: 'success' | 'error', message: string }

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!content.trim()) {
      setStatus({ type: 'error', message: 'Content cannot be empty.' });
      return;
    }

    setLoading(true);
    setStatus(null);

    try {
      const response = await fetch('http://localhost:5000/api/knowledge', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          items: [
            {
              content: content.trim(),
              metadata: {
                category: category.trim() || 'general',
                timestamp: new Date().toISOString()
              }
            }
          ]
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Failed to add knowledge');
      }

      setStatus({ type: 'success', message: `Successfully added ${data.added || 1} context entry to the ChromaDB Vector Store!` });
      setContent('');
      setCategory('');
    } catch (err) {
      setStatus({ type: 'error', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 w-full max-w-[1600px] mx-auto relative">
      <TopBar title="RAG Knowledge Ingestion" subtitle="Directly feed context documents into the AI's ChromaDB Vector Store" />

      <div className="grid lg:grid-cols-2 gap-8">
        
        {/* Input Form */}
        <Card delay={1} className="overflow-hidden flex flex-col">
          <div className="px-8 py-6 border-b border-[#3f5063] flex justify-between items-center bg-[rgba(33,185,120,0.05)]">
            <div className="flex items-center gap-3">
              <Database className="w-5 h-5 text-[#21b978]" />
              <h3 className="text-[18px] font-light text-white">Add Context Entry</h3>
            </div>
          </div>
          
          <div className="p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              
              <div>
                <label className="block text-[13px] text-[#c0cdd8] mb-2 font-medium">Knowledge Content</label>
                <textarea 
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="e.g., 'To reset a user PIN, the customer must navigate to Settings > Security > Reset PIN and enter the OTP sent to their registered mobile number.'"
                  className="w-full h-32 bg-[#151e28] border border-[#3f5063] rounded-xl p-4 text-white text-[14px] font-light placeholder-[#6b7a8a] focus:outline-none focus:border-[#21b978] trans resize-none"
                />
                <p className="text-[11px] text-[#8fa5b8] mt-2">This text will be chunked, embedded, and added to the RAG pipeline.</p>
              </div>

              <div>
                <label className="block text-[13px] text-[#c0cdd8] mb-2 font-medium">Metadata: Category (Optional)</label>
                <input 
                  type="text"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  placeholder="e.g., troubleshooting, faq, policy"
                  className="w-full bg-[#151e28] border border-[#3f5063] rounded-xl p-4 text-white text-[14px] font-light placeholder-[#6b7a8a] focus:outline-none focus:border-[#21b978] trans"
                />
              </div>

              <button 
                type="submit"
                disabled={loading}
                className={`w-full py-4 rounded-xl text-[14px] font-semibold text-[#151e28] flex items-center justify-center gap-2 trans ${
                  loading ? 'bg-[#1a9a63] opacity-70 cursor-not-allowed' : 'bg-[#21b978] hover:bg-[#28d189] shadow-[0_0_15px_rgba(33,185,120,0.3)]'
                }`}
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Ingesting into Vector Store...
                  </>
                ) : (
                  <>
                    <Plus className="w-5 h-5" />
                    Add to ChromaDB
                  </>
                )}
              </button>

              {status && (
                <div className={`p-4 rounded-lg flex items-start gap-3 border ${
                  status.type === 'success' ? 'bg-[rgba(33,185,120,0.1)] border-[rgba(33,185,120,0.2)] text-[#21b978]' : 'bg-[rgba(234,88,12,0.1)] border-[rgba(234,88,12,0.2)] text-[#ea580c]'
                }`}>
                  {status.type === 'success' ? <CheckCircle2 className="w-5 h-5 flex-shrink-0 mt-0.5" /> : <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />}
                  <p className="text-[14px]">{status.message}</p>
                </div>
              )}

            </form>
          </div>
        </Card>

        {/* Info Panel */}
        <Card delay={2} className="overflow-hidden flex flex-col bg-[#151e28]">
          <div className="px-8 py-6 border-b border-[#3f5063]">
            <h3 className="text-[18px] font-light text-white">How it Works</h3>
          </div>
          <div className="p-8 space-y-6">
            <div>
              <h4 className="text-[15px] font-medium text-white mb-2">1. Vector Embeddings</h4>
              <p className="text-[13px] text-[#8fa5b8] leading-relaxed">
                When you submit content, the Python backend converts the text into high-dimensional vector embeddings using an embedding model.
              </p>
            </div>
            <div>
              <h4 className="text-[15px] font-medium text-white mb-2">2. ChromaDB Storage</h4>
              <p className="text-[13px] text-[#8fa5b8] leading-relaxed">
                The vectors, along with the metadata payload, are stored directly in the Chroma vector database. It persists this data automatically.
              </p>
            </div>
            <div>
              <h4 className="text-[15px] font-medium text-white mb-2">3. Retrieval-Augmented Generation (RAG)</h4>
              <p className="text-[13px] text-[#8fa5b8] leading-relaxed">
                The next time a user asks a question via the Guidance Agent, the AI will perform a semantic search against ChromaDB, retrieve this exact context, and use it to answer the question accurately without hallucinating.
              </p>
            </div>
          </div>
        </Card>

      </div>
    </div>
  );
}
