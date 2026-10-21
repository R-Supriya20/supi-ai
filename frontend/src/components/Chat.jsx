import { useEffect, useRef, useState } from "react";
import axios from "axios";
import jsPDF from "jspdf";
import "./Chat.css";

const API_URL = "http://127.0.0.1:8000/chat";
const PROMPTS = [
  "How do I reset my password?",
  "How can I update my account details?",
  "Explain your refund policy",
];

function createConversationId() {
  return window.crypto?.randomUUID?.() || `conversation_${Date.now()}`;
}

function getSavedMessages(conversationId) {
  try {
    return JSON.parse(localStorage.getItem(`support_messages_${conversationId}`) || "[]");
  } catch {
    return [];
  }
}

export default function Chat() {
  const [conversationId, setConversationId] = useState(() => {
    let id = localStorage.getItem("support_conversation_id");
    if (!id) {
      id = createConversationId();
      localStorage.setItem("support_conversation_id", id);
    }
    return id;
  });
  const [messages, setMessages] = useState(() => {
    const id = localStorage.getItem("support_conversation_id");
    return id ? getSavedMessages(id) : [];
  });
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const textareaRef = useRef(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    localStorage.setItem("support_conversation_id", conversationId);
    localStorage.setItem(`support_messages_${conversationId}`, JSON.stringify(messages));
  }, [conversationId, messages]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  const startNewChat = () => {
    const newId = createConversationId();
    setConversationId(newId);
    setMessages([]);
    setInput("");
    setError("");
    textareaRef.current?.focus();
  };

  const sendMessage = async (text = input) => {
    const question = text.trim();
    if (!question || loading) return;

    const token = localStorage.getItem("access_token");
    if (!token) {
      setError("Your login session was not found. Please sign in again.");
      return;
    }

    const userMessage = {
      id: `${Date.now()}-user`,
      role: "user",
      content: question,
    };
    setMessages((current) => [...current, userMessage]);
    setInput("");
    setError("");
    setLoading(true);

    try {
      const response = await axios.post(
        API_URL,
        { question, conversation_id: conversationId },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const data = response.data || {};
      const assistantMessage = {
        id: `${Date.now()}-assistant`,
        role: "assistant",
        content: data.answer || "I couldn't generate an answer. Please try again.",
        sources: Array.isArray(data.sources) ? data.sources : [],
      };
      setMessages((current) => [...current, assistantMessage]);
    } catch (err) {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail;
      setError(
        status === 401
          ? "Your session has expired. Please sign in again."
          : typeof detail === "string"
            ? detail
            : "I couldn't connect to the support service. Check that the FastAPI backend is running and try again."
      );
    } finally {
      setLoading(false);
      textareaRef.current?.focus();
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const downloadConversation = () => {
    if (!messages.length) return;
    const pdf = new jsPDF({ unit: "pt", format: "a4" });
    const margin = 44;
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const maxWidth = pageWidth - margin * 2;
    let y = margin;

    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(18);
    pdf.text("AI Customer Support", margin, y);
    y += 24;
    pdf.setFont("helvetica", "normal");
    pdf.setFontSize(9);
    pdf.setTextColor(105, 112, 120);
    pdf.text(`Conversation exported ${new Date().toLocaleString()}`, margin, y);
    y += 25;
    pdf.setTextColor(30, 35, 42);

    messages.forEach((message) => {
      const label = message.role === "user" ? "You" : "AI Support";
      const content = String(message.content || "");
      const lines = pdf.splitTextToSize(content, maxWidth);
      const blockHeight = 19 + lines.length * 14 + 14;
      if (y + blockHeight > pageHeight - margin) {
        pdf.addPage();
        y = margin;
      }
      pdf.setFont("helvetica", "bold");
      pdf.setFontSize(10);
      pdf.text(label, margin, y);
      y += 15;
      pdf.setFont("helvetica", "normal");
      pdf.setFontSize(10);
      pdf.text(lines, margin, y);
      y += lines.length * 14 + 15;

      if (message.sources?.length) {
        pdf.setFont("helvetica", "italic");
        pdf.setFontSize(8);
        const sourceText = `Sources: ${message.sources.map((s) => s.document).filter(Boolean).join(", ")}`;
        const sourceLines = pdf.splitTextToSize(sourceText, maxWidth);
        if (y + sourceLines.length * 11 > pageHeight - margin) {
          pdf.addPage();
          y = margin;
        }
        pdf.text(sourceLines, margin, y);
        y += sourceLines.length * 11 + 12;
      }
      pdf.setDrawColor(230, 233, 237);
      pdf.line(margin, y - 5, pageWidth - margin, y - 5);
    });

    pdf.save("ai-customer-support-conversation.pdf");
  };

  return (
    <div className="support-app">
      {sidebarOpen && (
        <aside className="support-sidebar">
          <div className="sidebar-topline">
            <button className="icon-button sidebar-toggle" onClick={() => setSidebarOpen(false)} aria-label="Collapse sidebar" title="Collapse sidebar">
              <span className="menu-glyph">☰</span>
            </button>
            <div className="brand-mark" aria-hidden="true"><span>✦</span></div>
          </div>

          <button className="new-chat-button" onClick={startNewChat}>
            <span className="plus-glyph">＋</span> <span>New chat</span>
          </button>

          <div className="sidebar-label">Recent</div>
          <button className="recent-chat active-recent" title="Current conversation">
            <span className="recent-icon">◷</span>
            <span className="recent-title">Customer support chat</span>
          </button>

          <div className="sidebar-spacer" />
          <div className="sidebar-help">
            <div className="help-icon">?</div>
            <div><strong>Need help?</strong><span>Ask your support assistant</span></div>
          </div>
          <div className="sidebar-footnote">AI Customer Support</div>
        </aside>
      )}

      <main className="support-main">
        <header className="support-header">
          <div className="header-left">
            {!sidebarOpen && (
              <button className="icon-button" onClick={() => setSidebarOpen(true)} aria-label="Open sidebar" title="Open sidebar">☰</button>
            )}
            <div className="header-brand"><span className="brand-mark small"><span>✦</span></span><span>Support AI</span></div>
            <span className="header-divider">/</span>
            <span className="header-current">Customer assistant</span>
          </div>
          <div className="header-actions">
            <span className="status-pill"><span className="status-dot" /> Online</span>
            <button className="export-button" onClick={downloadConversation} disabled={!messages.length} title="Download the full conversation as PDF">
              <span aria-hidden="true">⇩</span> <span className="export-label">Export chat</span>
            </button>
            <div className="profile-avatar" title="Your account">U</div>
          </div>
        </header>

        <section className={`chat-stage ${messages.length ? "has-messages" : "welcome-stage"}`}>
          {messages.length === 0 ? (
            <div className="welcome-content">
              <div className="welcome-orb"><span>✦</span></div>
              <p className="eyebrow">YOUR PERSONAL SUPPORT ASSISTANT</p>
              <h1>How can I help <span>you today?</span></h1>
              <p className="welcome-subtitle">Ask a question about your account, products, or support documents.</p>
              <div className="prompt-grid">
                {PROMPTS.map((prompt, index) => (
                  <button className="prompt-card" key={prompt} onClick={() => sendMessage(prompt)} disabled={loading}>
                    <span className={`prompt-symbol prompt-symbol-${index}`}>{["↻", "♙", "◇"][index]}</span>
                    <span>{prompt}</span>
                    <span className="prompt-arrow">↗</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="message-list">
              {messages.map((message) => (
                <article key={message.id} className={`message-row ${message.role === "user" ? "user-row" : "assistant-row"}`}>
                  {message.role === "assistant" && <div className="message-avatar assistant-avatar"><span>✦</span></div>}
                  <div className={`message-content ${message.role === "user" ? "user-bubble" : "assistant-bubble"}`}>
                    {message.role === "assistant" && <div className="message-author">Support AI</div>}
                    <div className="message-text">{message.content}</div>
                    {message.sources?.length > 0 && (
                      <div className="source-area">
                        <div className="source-heading">Sources used</div>
                        <div className="source-list">
                          {message.sources.map((source, index) => (
                            <div className="source-chip" key={`${source.document || "source"}-${index}`}>
                              <span className="source-file-icon">▤</span>
                              <span>{source.document || `Document ${index + 1}`}</span>
                              {Number.isFinite(Number(source.score)) && <small>{Number(source.score).toFixed(2)}</small>}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  {message.role === "user" && <div className="message-avatar user-avatar">U</div>}
                </article>
              ))}
              {loading && (
                <article className="message-row assistant-row">
                  <div className="message-avatar assistant-avatar"><span>✦</span></div>
                  <div className="typing-card"><span className="typing-dots"><i /><i /><i /></span><span>Finding the best answer…</span></div>
                </article>
              )}
              <div ref={bottomRef} />
            </div>
          )}
        </section>

        <footer className="composer-area">
          {error && <div className="error-banner" role="alert"><span>!</span>{error}</div>}
          <div className="composer-box">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask your support question…"
              rows={1}
              aria-label="Your message"
              disabled={loading}
            />
            <div className="composer-toolbar">
              <div className="composer-hint"><span className="keyboard-icon">↵</span> Enter to send <span className="hint-separator">·</span> Shift + Enter for a new line</div>
              <button className="send-button" onClick={() => sendMessage()} disabled={!input.trim() || loading} aria-label="Send message" title="Send message">
                {loading ? <span className="send-spinner" /> : <span>↑</span>}
              </button>
            </div>
          </div>
          <p className="disclaimer">AI can make mistakes. Check important information with your support team.</p>
        </footer>
      </main>
    </div>
  );
}
