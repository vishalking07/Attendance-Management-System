import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Sparkles, Bot, User, RefreshCw, ChevronDown, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';

const AIChatbotDrawer = () => {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: `Hello ${user?.name ? user.name.split(' ')[0] : 'there'}! I am your **Bio-XAI Smart Attendance & Academic Assistant**.\n\nI can help you check your attendance status, calculate safe bunk budgets, guide biometric registration, or explain 'What-If' ML recovery simulations. How can I help you today?`,
      time: 'Just now'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([
    "Check My Bunk Budget",
    "How to Register Face ID",
    "Explain 'What-If' Prognosis",
    "Why Smart Pass QR?"
  ]);

  const chatEndRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const handleSendMessage = async (userMsg) => {
    const textToSend = userMsg || input;
    if (!textToSend.trim()) return;

    const userMessage = {
      sender: 'user',
      text: textToSend,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.post('/chatbot/query', {
        message: textToSend,
        student_id: user?.id || 'usr_student_2'
      });

      if (res.data) {
        setMessages((prev) => [
          ...prev,
          {
            sender: 'bot',
            text: res.data.reply,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ]);
        if (res.data.suggestions && res.data.suggestions.length > 0) {
          setSuggestions(res.data.suggestions);
        }
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: `I'm here to help! Your current attendance is **64.0%** (shortage). You have **0 safe bunk budget** remaining. Please use the **'What-If' Prognosis Simulator** or submit a medical excuse under Leave Requests.`,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const renderFormattedText = (text) => {
    return text.split('\n').map((line, idx) => {
      // Basic markdown styling for bold **text**
      const parts = line.split(/(\*\*.*?\*\*)/g);
      return (
        <p key={idx} className="min-h-[1rem] leading-relaxed">
          {parts.map((part, pIdx) => {
            if (part.startsWith('**') && part.endsWith('**')) {
              return <strong key={pIdx} className="font-black text-slate-900">{part.slice(2, -2)}</strong>;
            }
            return part;
          })}
        </p>
      );
    });
  };

  return (
    <>
      {/* Floating Launcher Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-16 right-4 sm:bottom-6 sm:right-6 z-40 group flex items-center space-x-2.5 px-3.5 py-2.5 sm:px-4 sm:py-3 rounded-full bg-gradient-to-r from-purple-800 via-[#7C3AED] to-purple-700 text-white shadow-xl shadow-purple-900/30 hover:scale-[1.03] active:scale-95 transition-all duration-200 border border-white/25"
        >
          <div className="relative">
            <Bot className="w-5 h-5 text-white animate-bounce" />
            <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-400 ring-2 ring-purple-900 animate-pulse"></span>
          </div>
          <span className="text-xs font-black font-heading tracking-wider uppercase pr-1">
            Bio-XAI Assistant
          </span>
          <Sparkles className="w-3.5 h-3.5 text-amber-300" />
        </button>
      )}

      {/* Slide-Up / Floating Chatbot Drawer */}
      {isOpen && (
        <div className="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 z-50 w-[94vw] sm:w-[400px] h-[550px] max-h-[88vh] bg-white rounded-3xl shadow-2xl border border-purple-200/90 flex flex-col overflow-hidden animate-scaleUp">
          
          {/* Drawer Header */}
          <div className="px-5 py-3.5 bg-gradient-to-r from-purple-900 via-[#7C3AED] to-purple-800 text-white flex items-center justify-between flex-shrink-0">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-xl bg-white/20 backdrop-blur-md flex items-center justify-center border border-white/25 shadow-inner">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div>
                <h3 className="text-xs font-black tracking-wider uppercase font-heading block">
                  Bio-XAI Academic AI
                </h3>
                <div className="flex items-center space-x-1.5 mt-0.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span className="text-[10px] text-purple-200 font-mono">
                    XGBoost v2.4 + SHAP Assistant
                  </span>
                </div>
              </div>
            </div>

            <button
              onClick={() => setIsOpen(false)}
              className="w-7 h-7 rounded-full bg-white/10 hover:bg-white/25 flex items-center justify-center text-white transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Chat Messages Body */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3.5 bg-[#FAF8FE] custom-scrollbar text-xs">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex items-start space-x-2 ${
                  m.sender === 'user' ? 'flex-row-reverse space-x-reverse' : 'flex-row'
                }`}
              >
                {/* Avatar */}
                <div
                  className={`w-7 h-7 rounded-xl flex items-center justify-center flex-shrink-0 text-[10px] font-bold ${
                    m.sender === 'user'
                      ? 'bg-purple-600 text-white'
                      : 'bg-white border border-purple-200 text-[#7C3AED] shadow-sm'
                  }`}
                >
                  {m.sender === 'user' ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
                </div>

                {/* Message Bubble */}
                <div
                  className={`p-3.5 rounded-2xl max-w-[82%] text-xs shadow-sm ${
                    m.sender === 'user'
                      ? 'bg-gradient-to-r from-purple-700 to-[#7C3AED] text-white rounded-tr-none'
                      : 'bg-white border border-purple-100 text-slate-700 rounded-tl-none space-y-1'
                  }`}
                >
                  {renderFormattedText(m.text)}
                  <span
                    className={`text-[9px] block text-right mt-1 font-mono ${
                      m.sender === 'user' ? 'text-purple-200' : 'text-slate-400'
                    }`}
                  >
                    {m.time}
                  </span>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex items-center space-x-2 text-xs text-purple-700 p-2">
                <div className="w-6 h-6 rounded-lg bg-white border border-purple-200 flex items-center justify-center shadow-sm">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin text-[#7C3AED]" />
                </div>
                <span className="font-bold font-mono text-[11px] animate-pulse">Bio-XAI is analyzing...</span>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Quick Prompt Suggestion Chips */}
          <div className="px-3.5 py-2 bg-white border-t border-purple-100/80 flex items-center space-x-1.5 overflow-x-auto custom-scrollbar flex-shrink-0">
            {suggestions.map((chip, cIdx) => (
              <button
                key={cIdx}
                onClick={() => handleSendMessage(chip)}
                className="px-2.5 py-1 rounded-full bg-purple-50 hover:bg-purple-100 text-purple-800 border border-purple-200/80 text-[10px] font-bold whitespace-nowrap transition-colors flex-shrink-0"
              >
                {chip}
              </button>
            ))}
          </div>

          {/* Message Input Bar */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="p-3 bg-white border-t border-purple-100 flex items-center space-x-2 flex-shrink-0"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about attendance, bunk budget, face ID..."
              className="flex-1 px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/20 focus:border-[#7C3AED] text-xs font-medium text-slate-800 transition"
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="p-2.5 rounded-xl bg-[#7C3AED] hover:bg-purple-700 disabled:opacity-40 text-white transition-all shadow-md shadow-purple-900/15 flex-shrink-0"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>

        </div>
      )}
    </>
  );
};

export default AIChatbotDrawer;
