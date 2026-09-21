import { useEffect, useRef, useState } from "react";
import { getChatHistory, sendChatMessage } from "../../services/api/agenticApi";

export default function CareerAssistant() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const endRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => { loadHistory(); }, []);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, sending]);

  async function loadHistory() {
    setLoading(true); setError("");
    try {
      const result = await getChatHistory();
      const history = Array.isArray(result?.messages) ? result.messages : [];
      setMessages(history.filter((item) => item.role === "user" || item.role === "assistant"));
    } catch (error) {
      console.error("Unable to load chat history:", error);
      setError(error?.message || "Unable to load conversation.");
    } finally { setLoading(false); }
  }

  async function submit(event) {
    event.preventDefault();
    const message = input.trim();
    if (!message || sending) return;
    setError("");
    setMessages((current) => [...current, { role: "user", content: message, timestamp: new Date().toISOString() }]);
    setInput("");
    resizeTextarea();
    setSending(true);
    try {
      const response = await sendChatMessage({ message });
      const content = extractAssistantMessage(response);
      if (!content) throw new Error("The CareerForge backend returned an empty or unexpected chat response.");
      setMessages((current) => [...current, { role: "assistant", content, timestamp: new Date().toISOString() }]);
    } catch (error) {
      console.error("Career Assistant failed:", error);
      setError(error?.message || "Unable to get a response from the AI assistant.");
    } finally { setSending(false); }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); }
  }
  function resizeTextarea() {
    if (!inputRef.current) return;
    inputRef.current.style.height = "auto";
    inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 180)}px`;
  }

  return (
    <div className="cf-page cf-assistant-page">
      <header className="cf-assistant-header">
        <div>
          <div className="cf-eyebrow">AI career workspace</div>
          <h1 className="cf-title">Career Assistant</h1>
          <p className="cf-muted cf-lead">A focused place to work through job descriptions, your profile, applications and professional outreach.</p>
        </div>
        <div className="cf-assistant-badge"><span /> AI assistant</div>
      </header>

      <section className="cf-assistant-shell cf-card">
        <div className="cf-assistant-intro">
          <div className="cf-assistant-big-icon"><SparkIcon /></div>
          <div>
            <strong>What can you use Career Assistant for?</strong>
            <p>Ask questions about a job description, understand how your profile matches a role, prepare professional outreach, or get help deciding your next application step.</p>
          </div>
        </div>

        <div className="cf-assistant-messages">
          {loading ? <div className="cf-chat-empty"><span className="cf-spinner" /><span>Loading your conversation...</span></div> : messages.length === 0 ? (
            <div className="cf-assistant-welcome">
              <div className="cf-assistant-welcome-icon"><SparkIcon /></div>
              <h2>Start with a career question</h2>
              <p>Try: “Analyse this role for me”, “What should I improve in my profile?” or “Help me draft a professional email.”</p>
            </div>
          ) : (
            <div className="cf-assistant-thread">
              {messages.map((message, index) => <FullMessage key={`${message.timestamp || "message"}-${index}`} message={message} />)}
              {sending && <div className="cf-full-row assistant"><div className="cf-chat-mini-avatar"><SparkIcon /></div><div><span className="cf-message-author">CareerForge AI</span><div className="cf-ai-bubble"><span /><span /><span /></div></div></div>}
              <div ref={endRef} />
            </div>
          )}
        </div>

        {error && <div className="cf-chat-error">{error}</div>}

        <form className="cf-assistant-form" onSubmit={submit}>
          <textarea ref={inputRef} value={input} onChange={(e) => { setInput(e.target.value); resizeTextarea(); }} onKeyDown={handleKeyDown} disabled={sending} rows={1} placeholder="Write your question or paste a job description..." />
          <button type="submit" disabled={sending || !input.trim()}><ArrowIcon /> <span>{sending ? "Thinking..." : "Send"}</span></button>
          <small>Enter to send · Shift + Enter for a new line</small>
        </form>
      </section>
    </div>
  );
}

function FullMessage({ message }) {
  const user = message.role === "user";
  return <div className={`cf-full-row ${user ? "user" : "assistant"}`}>{!user && <div className="cf-chat-mini-avatar"><SparkIcon /></div>}<div className="cf-full-message-wrap"><span className="cf-message-author">{user ? "You" : "CareerForge AI"}</span><div className={`cf-full-message ${user ? "user" : "assistant"}`}>{message.content}</div></div></div>;
}
function extractAssistantMessage(response) { if (typeof response === "string") return response.trim(); if (!response || typeof response !== "object") return ""; const direct = response.message ?? response.response ?? response.answer ?? response.content ?? response.text; if (typeof direct === "string" && direct.trim()) return direct.trim(); if (response.data && typeof response.data === "object") { const nested = response.data.message ?? response.data.response ?? response.data.answer ?? response.data.content ?? response.data.text; if (typeof nested === "string" && nested.trim()) return nested.trim(); } if (Array.isArray(response.messages)) { const list = response.messages.filter((m) => m?.role === "assistant"); const last = list[list.length - 1]; return typeof last?.content === "string" ? last.content.trim() : typeof last?.message === "string" ? last.message.trim() : ""; } return ""; }
function SparkIcon() { return <svg viewBox="0 0 24 24" fill="none"><path d="m12 3 1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7L12 3Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round"/><path d="m19 16 .8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8L19 16Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round"/></svg>; }
function ArrowIcon() { return <svg viewBox="0 0 24 24" fill="none"><path d="m4 12 15-7-4 14-3.2-6L4 12Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round"/><path d="m11.8 13 4.4-4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/></svg>; }
