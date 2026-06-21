import { useState, useRef, useEffect } from 'react';
import { Bot, Send, User } from 'lucide-react';
import api from '../lib/api';
import type { ChatMessage } from '../lib/types';

export function AICopilot() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 1,
      role: 'assistant',
      content: 'I am the ASTRA Copilot. How can I assist you with traffic management today?',
      suggested: ['Show high risk events', 'Analyze corridor stress']
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async (text: string) => {
    if (!text.trim()) return;

    const userMsg: ChatMessage = { id: Date.now(), role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await api.post('/chat', { message: text });
      const botMsg: ChatMessage = { 
        id: Date.now() + 1, 
        role: 'assistant', 
        content: response.data.response || 'Sorry, I did not understand that.', 
        suggested: response.data.suggested_actions || [] 
      };
      setMessages(prev => [...prev, botMsg]);
      setIsTyping(false);
    } catch (error) {
      console.error('Chat API failed, using fallback mock:', error);
      // Simulate API
      setTimeout(() => {
        const botMsg: ChatMessage = { id: Date.now() + 1, role: 'assistant', content: '', suggested: [] };
        const q = text.toLowerCase();
        
        if (q.includes('vip')) {
          botMsg.content = 'For VIP movements, ASTRA recommends prioritizing corridor clearance and pre-deploying 30 minutes ahead of the schedule. I\'ve found 12 similar past events on this route. Would you like to review them?';
          botMsg.suggested = ['View similar VIP events', 'Generate deployment plan'];
        } else if (q.includes('accident')) {
          botMsg.content = 'Major accidents during peak hours typically take 60-90 minutes to clear. Ensure the nearest trauma center route is clear.';
          botMsg.suggested = ['Check nearest hospitals', 'Optimize resource allocation'];
        } else {
          botMsg.content = 'I can help you analyze traffic patterns, suggest deployment strategies, or look up historical resolutions for similar incidents.';
          botMsg.suggested = ['Predict resolution time', 'Show active barricade count'];
        }

        setMessages(prev => [...prev, botMsg]);
        setIsTyping(false);
      }, 1500);
    }
  };

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center">
          <Bot className="w-8 h-8 mr-3 text-indigo-600" />
          ASTRA Copilot
        </h1>
        <p className="text-sm text-slate-500 mt-1">Your AI assistant for traffic decision making and situational awareness.</p>
      </div>

      <div className="flex-1 bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col overflow-hidden">
        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`flex max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                
                {/* Avatar */}
                <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${
                  msg.role === 'user' ? 'bg-indigo-100 text-indigo-600 ml-3' : 'bg-slate-900 text-white mr-3'
                }`}>
                  {msg.role === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </div>
                
                {/* Message Bubble */}
                <div className="flex flex-col">
                  <div className={`p-4 rounded-2xl ${
                    msg.role === 'user' 
                      ? 'bg-indigo-600 text-white rounded-tr-sm' 
                      : 'bg-slate-50 border border-slate-200 text-slate-800 rounded-tl-sm'
                  }`}>
                    <p className="text-sm leading-relaxed">{msg.content}</p>
                  </div>
                  
                  {/* Suggestions */}
                  {msg.suggested && msg.suggested.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-3">
                      {msg.suggested.map((sug, i) => (
                        <button 
                          key={i} 
                          onClick={() => handleSend(sug)} 
                          className="text-xs font-medium bg-white border border-indigo-200 text-indigo-600 px-3 py-1.5 rounded-full hover:bg-indigo-50 transition-colors"
                        >
                          {sug}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="flex justify-start">
              <div className="flex max-w-[80%] flex-row">
                <div className="flex-shrink-0 h-8 w-8 rounded-full bg-slate-900 text-white mr-3 flex items-center justify-center">
                  <Bot className="h-4 w-4" />
                </div>
                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 text-slate-800 rounded-tl-sm flex items-center space-x-1">
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-white border-t border-slate-200">
          <form 
            onSubmit={(e) => {
              e.preventDefault();
              handleSend(input);
            }} 
            className="relative flex items-center"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Copilot about an event, corridor, or strategy..."
              className="w-full pl-4 pr-12 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-slate-50 text-sm"
            />
            <button 
              type="submit" 
              disabled={!input.trim() || isTyping}
              className="absolute right-2 p-2 text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
          <div className="text-center mt-2">
            <span className="text-[10px] text-slate-400">ASTRA Copilot can make mistakes. Verify critical deployment decisions.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
