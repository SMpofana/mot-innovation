'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { knowledgeBase, quickReplies, type KnowledgeEntry } from '../chatbot-knowledge';

interface Message {
  role: 'bot' | 'user';
  text: string;
  timestamp: number;
}

// Simple keyword-matching engine to find the best knowledge base entry
function findBestAnswer(input: string): KnowledgeEntry | null {
  const normalized = input.toLowerCase();
  let bestScore = 0;
  let bestEntry: KnowledgeEntry | null = null;

  for (const entry of knowledgeBase) {
    let score = 0;
    for (const keyword of entry.keywords) {
      if (normalized.includes(keyword)) {
        // Longer keyword matches get higher weight
        score += keyword.length > 6 ? 3 : keyword.length > 3 ? 2 : 1;
      }
    }
    // Category bonus
    if (normalized.includes(entry.category)) score += 1;
    if (score > bestScore) {
      bestScore = score;
      bestEntry = entry;
    }
  }

  return bestScore > 0 ? bestEntry : null;
}

export default function Chatbot() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'bot',
      text: "Hi! I'm M.O.T — your marketing intelligence assistant. I can answer questions about digital asset management, multi-channel delivery, performance tracking, campaign optimization, and pricing. What's on your mind?",
      timestamp: Date.now(),
    },
  ]);
  const [input, setInput] = useState('');
  const [typing, setTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, typing]);

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 300);
    }
  }, [open]);

  const sendMessage = (text: string) => {
    if (!text.trim()) return;

    const userMsg: Message = { role: 'user', text, timestamp: Date.now() };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setTyping(true);

    // Simulate thinking + response
    setTimeout(() => {
      const entry = findBestAnswer(text);
      const response = entry
        ? entry.answer
        : "I'm not sure I caught that. Try asking about: scattered assets, manual social media posting, reporting headaches, wasted ad spend, pricing, or what we do. You can also book a free consultation and we'll map your entire marketing infrastructure.";

      setMessages((prev) => [...prev, { role: 'bot', text: response, timestamp: Date.now() }]);
      setTyping(false);
    }, 800 + Math.random() * 600);
  };

  const handleQuickReply = (reply: string) => {
    sendMessage(reply);
  };

  return (
    <>
      {/* Floating button — cream/white on dark */}
      <motion.button
        onClick={() => setOpen(!open)}
        className="fixed bottom-6 right-6 z-50"
        style={{
          width: '3.5rem',
          height: '3.5rem',
          borderRadius: '50%',
          background: 'var(--bg-cream)',
          color: 'var(--bg)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          border: '1px solid var(--border)',
          cursor: 'pointer',
        }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        aria-label="Open chat assistant"
      >
        <AnimatePresence mode="wait">
          {open ? (
            <motion.svg
              key="close"
              width="22"
              height="22"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 90, opacity: 0 }}
            >
              <path d="M6 18L18 6M6 6l12 12" strokeLinecap="round" strokeLinejoin="round" />
            </motion.svg>
          ) : (
            <motion.svg
              key="chat"
              width="22"
              height="22"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              initial={{ rotate: 90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: -90, opacity: 0 }}
            >
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" strokeLinecap="round" strokeLinejoin="round" />
            </motion.svg>
          )}
        </AnimatePresence>
      </motion.button>

      {/* Chat panel — dark, monochrome */}
      <AnimatePresence>
        {open && (
          <motion.div
            className="fixed bottom-24 right-6 z-50"
            style={{
              width: 'min(380px, calc(100vw - 3rem))',
              height: 'min(560px, calc(100vh - 8rem))',
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: '0.75rem',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
            }}
            initial={{ opacity: 0, y: 15, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 15, scale: 0.97 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
          >
            {/* Header — minimal dark */}
            <div
              style={{
                padding: '1rem 1.25rem',
                background: 'var(--bg-alt)',
                borderBottom: '1px solid var(--border)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
              }}
            >
              <div
                style={{
                  width: '2rem',
                  height: '2rem',
                  borderRadius: '50%',
                  border: '1px solid var(--border)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.7rem',
                  fontWeight: 400,
                  color: 'var(--text)',
                  letterSpacing: '0.02em',
                }}
              >
                M.O.T
              </div>
              <div>
                <div
                  style={{
                    fontWeight: 400,
                    fontSize: '0.85rem',
                    color: 'var(--text)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.06em',
                  }}
                >
                  Marketing Assistant
                </div>
                <div
                  style={{
                    fontSize: '0.7rem',
                    color: 'var(--text-muted)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.3rem',
                  }}
                >
                  <span
                    style={{
                      width: 6,
                      height: 6,
                      borderRadius: '50%',
                      background: 'var(--text)',
                      display: 'inline-block',
                    }}
                  />
                  Online
                </div>
              </div>
            </div>

            {/* Messages */}
            <div
              style={{
                flex: 1,
                overflowY: 'auto',
                padding: '1rem 1.25rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.75rem',
              }}
            >
              {messages.map((msg, i) => (
                <motion.div
                  key={i}
                  style={{
                    alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    maxWidth: '85%',
                  }}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.25 }}
                >
                  <div
                    style={{
                      padding: '0.7rem 1rem',
                      borderRadius: msg.role === 'user' ? '0.625rem 0.625rem 0.25rem 0.625rem' : '0.625rem 0.625rem 0.625rem 0.25rem',
                      background: msg.role === 'user' ? 'var(--bg-cream)' : 'var(--bg-alt)',
                      color: msg.role === 'user' ? 'var(--text-dark)' : 'var(--text)',
                      fontSize: '0.85rem',
                      lineHeight: 1.5,
                      whiteSpace: 'pre-wrap',
                      fontWeight: 400,
                    }}
                  >
                    {msg.text}
                  </div>
                </motion.div>
              ))}

              {/* Typing indicator */}
              {typing && (
                <motion.div
                  style={{ alignSelf: 'flex-start' }}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <div
                    style={{
                      padding: '0.75rem 1rem',
                      borderRadius: '0.625rem 0.625rem 0.625rem 0.25rem',
                      background: 'var(--bg-alt)',
                      display: 'flex',
                      gap: '0.3rem',
                    }}
                  >
                    {[0, 1, 2].map((dot) => (
                      <motion.span
                        key={dot}
                        style={{
                          width: 6,
                          height: 6,
                          borderRadius: '50%',
                          background: 'var(--text-muted)',
                        }}
                        animate={{ opacity: [0.3, 1, 0.3] }}
                        transition={{ duration: 1, repeat: Infinity, delay: dot * 0.2 }}
                      />
                    ))}
                  </div>
                </motion.div>
              )}

              {/* Quick replies (show when few messages) */}
              {messages.length <= 1 && !typing && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.5rem' }}>
                  {quickReplies.map((reply, i) => (
                    <motion.button
                      key={i}
                      onClick={() => handleQuickReply(reply)}
                      style={{
                        padding: '0.45rem 0.8rem',
                        borderRadius: '0.375rem',
                        background: 'transparent',
                        color: 'var(--text)',
                        border: '1px solid var(--border)',
                        fontSize: '0.75rem',
                        fontWeight: 400,
                        cursor: 'pointer',
                      }}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 + i * 0.06 }}
                      whileHover={{ borderColor: 'var(--text-muted)' }}
                      whileTap={{ scale: 0.97 }}
                    >
                      {reply}
                    </motion.button>
                  ))}
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input — minimal */}
            <div
              style={{
                padding: '0.75rem 1rem',
                borderTop: '1px solid var(--border)',
                display: 'flex',
                gap: '0.5rem',
              }}
            >
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') sendMessage(input);
                }}
                placeholder="Ask about assets, delivery, reporting..."
                style={{
                  flex: 1,
                  fontSize: '0.85rem',
                  padding: '0.625rem 0.875rem',
                  background: 'var(--bg)',
                  border: '1px solid var(--border)',
                  borderRadius: '0.375rem',
                  color: 'var(--text)',
                  outline: 'none',
                }}
              />
              <button
                onClick={() => sendMessage(input)}
                style={{
                  padding: '0.625rem 1rem',
                  fontSize: '0.85rem',
                  background: 'var(--bg-cream)',
                  color: 'var(--bg)',
                  border: 'none',
                  borderRadius: '0.375rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
                aria-label="Send message"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}