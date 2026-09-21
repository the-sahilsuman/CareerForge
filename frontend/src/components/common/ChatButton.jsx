import { useEffect, useRef, useState } from "react";
import { getChatHistory, sendChatMessage } from "../../services/api/agenticApi";

function extractAssistantMessage(response) {
  if (typeof response === "string") return response.trim();
  if (!response || typeof response !== "object") return "";

  const direct = response.message ?? response.response ?? response.answer ?? response.content ?? response.text;
  if (typeof direct === "string" && direct.trim()) return direct.trim();

  if (response.data && typeof response.data === "object") {
    const nested = response.data.message ?? response.data.response ?? response.data.answer ?? response.data.content ?? response.data.text;
    if (typeof nested === "string" && nested.trim()) return nested.trim();
  }

  if (Array.isArray(response.messages)) {
    const assistants = response.messages.filter((item) => item?.role === "assistant");
    const last = assistants[assistants.length - 1];
    if (typeof last?.content === "string" && last.content.trim()) return last.content.trim();
    if (typeof last?.message === "string" && last.message.trim()) return last.message.trim();
  }
  return "";
}

export default function ChatButton() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (open) loadHistory();
  }, [open]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function loadHistory() {
    setHistoryLoading(true);
    setError("");
    try {
      const result = await getChatHistory();
      const history = Array.isArray(result?.messages) ? result.messages : [];
      setMessages(history.filter((message) => message.role === "user" || message.role === "assistant"));
    } catch (error) {
      console.error("Unable to load chat history:", error);
      setError(error?.message || "Unable to load conversation.");
    } finally {
      setHistoryLoading(false);
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const message = input.trim();
    if (!message || loading) return;

    setError("");
    setMessages((current) => [...current, { role: "user", content: message, timestamp: new Date().toISOString() }]);
    setInput("");
    setLoading(true);

    try {
      const response = await sendChatMessage({ message });
      const assistantMessage = extractAssistantMessage(response);
      if (!assistantMessage) throw new Error("The CareerForge backend returned an empty or unexpected chat response.");
      setMessages((current) => [...current, { role: "assistant", content: assistantMessage, timestamp: new Date().toISOString() }]);
    } catch (error) {
      console.error("Agent chat failed:", error);
      setError(error?.message || "Unable to get a response from the AI assistant.");
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      event.currentTarget.form?.requestSubmit();
    }
  }

  return (
    <>
      {open && (
        <section className="cf-chat-panel" aria-label="Career Assistant">
          <header className="cf-chat-header">
            <div className="cf-chat-avatar"><SparkIcon /></div>
            <div>
              <strong>Career Assistant</strong>
              <span>Ask about your profile, jobs or applications</span>
            </div>
            <button type="button" className="cf-chat-close" onClick={() => setOpen(false)} aria-label="Close assistant">×</button>
          </header>

          <div className="cf-chat-messages">
            {historyLoading ? (
              <div className="cf-chat-empty"><Spinner /> <span>Loading conversation...</span></div>
            ) : messages.length === 0 ? (
              <div className="cf-chat-empty">
                <div className="cf-chat-empty-icon"><SparkIcon /></div>
                <strong>How can I help?</strong>
                <span>Ask for help with your career, profile or job applications.</span>
              </div>
            ) : (
              <div className="cf-chat-thread">
                {messages.map((message, index) => <ChatMessage key={`${message.timestamp || "message"}-${index}`} message={message} />)}
                {loading && <div className="cf-chat-row"><div className="cf-ai-bubble"><span /><span /><span /></div></div>}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {error && <div className="cf-chat-error">{error}</div>}

          <form onSubmit={handleSubmit} className="cf-chat-form">
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              rows={1}
              placeholder="Ask for help..."
              className="cf-chat-input"
            />
            <button type="submit" disabled={loading || !input.trim()} className="cf-chat-send" aria-label="Send message"><ArrowIcon /></button>
            <span className="cf-chat-hint">Enter to send · Shift + Enter for a new line</span>
          </form>
        </section>
      )}

      <div className={`cf-chat-launcher ${open ? "open" : ""}`}>
        {!open && <span className="cf-chat-label">Ask for help</span>}
        <button type="button" onClick={() => setOpen((value) => !value)} aria-label={open ? "Close Career Assistant" : "Open Career Assistant"}>
          {open ? <CloseIcon /> : <SparkIcon />}
        </button>
      </div>
    </>
  );
}

function ChatMessage({ message }) {
  const isUser = message.role === "user";
  return (
    <div className={`cf-chat-row ${isUser ? "user" : "assistant"}`}>
      {!isUser && <div className="cf-chat-mini-avatar"><SparkIcon /></div>}
      <div className={`cf-message-wrap ${isUser ? "user" : "assistant"}`}>
        <span className="cf-message-author">{isUser ? "You" : "CareerForge AI"}</span>
        <div className={`cf-message ${isUser ? "user" : "assistant"}`}>{message.content}</div>
      </div>
    </div>
  );
}

function Spinner() { return <span className="cf-spinner" />; }
function SparkIcon() { return <svg viewBox="0 0 24 24" fill="none"><path d="m12 3 1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7L12 3Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round"/><path d="m19 16 .8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8L19 16Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round"/></svg>; }
function ArrowIcon() { return <svg viewBox="0 0 24 24" fill="none"><path d="m4 12 15-7-4 14-3.2-6L4 12Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round"/><path d="m11.8 13 4.4-4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/></svg>; }
function CloseIcon() { return <svg viewBox="0 0 24 24" fill="none"><path d="m6 6 12 12M18 6 6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg>; }
