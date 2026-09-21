import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../../auth/AuthProvider";
import { getProfile } from "../../services/api/profileApi";
import { getEmailRecords } from "../../services/api/emailApi";
import { getBuckets, createBucket, updateBucket, deleteBucket } from "../../services/api/bucketApi";
import { getEmailConnections } from "../../services/api/emailConnectionApi";

export default function UserDashboard() {
  const { user, backendUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [emails, setEmails] = useState([]);
  const [buckets, setBuckets] = useState([]);
  const [emailConnected, setEmailConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [selectedBucket, setSelectedBucket] = useState(null);
  const [showAllEmails, setShowAllEmails] = useState(false);
  const [showAllBuckets, setShowAllBuckets] = useState(false);
  const [showBucketForm, setShowBucketForm] = useState(false);
  const [editingBucket, setEditingBucket] = useState(null);
  const [bucketSaving, setBucketSaving] = useState(false);
  const [bucketForm, setBucketForm] = useState({ title: "", description: "", type: "TASK" });

  useEffect(() => { loadDashboard(); }, []);

  async function loadDashboard() {
    setLoading(true);
    setError("");
    const [profileResult, emailResult, bucketResult, connectionResult] = await Promise.allSettled([
      getProfile(), getEmailRecords(), getBuckets(), getEmailConnections(),
    ]);

    if (profileResult.status === "fulfilled") setProfile(profileResult.value);
    else console.error("Unable to load profile:", profileResult.reason);

    if (emailResult.status === "fulfilled") setEmails(Array.isArray(emailResult.value) ? emailResult.value : []);
    else setError(emailResult.reason?.message || "Unable to load email records.");

    if (bucketResult.status === "fulfilled") setBuckets(Array.isArray(bucketResult.value) ? bucketResult.value : []);
    else setError(bucketResult.reason?.message || "Unable to load buckets.");

    if (connectionResult.status === "fulfilled") {
      const connections = Array.isArray(connectionResult.value) ? connectionResult.value : [];
      setEmailConnected(connections.length > 0);
    } else {
      console.error("Unable to load email connection:", connectionResult.reason);
      setEmailConnected(false);
    }
    setLoading(false);
  }

  const sortedEmails = useMemo(() => [...emails].sort((a,b) => new Date(b.sent_at || b.created_at || 0) - new Date(a.sent_at || a.created_at || 0)), [emails]);
  const sortedBuckets = useMemo(() => [...buckets].sort((a,b) => new Date(b.updated_at || b.created_at || 0) - new Date(a.updated_at || a.created_at || 0)), [buckets]);
  const completedBuckets = buckets.filter((bucket) => bucket.status === "DONE").length;
  const userName = profile ? [profile.first_name, profile.last_name].filter(Boolean).join(" ") : (user?.attributes?.name || user?.attributes?.given_name || user?.username || "there");
  const username = user?.username || backendUser?.user_id || "—";
  const location = profile?.location || "Location not added";
  const professionalEmail = profile?.professional_email || "Professional email not added";

  function openAddBucket() {
    setEditingBucket(null);
    setBucketForm({ title: "", description: "", type: "TASK" });
    setShowBucketForm(true);
  }

  function openEditBucket(bucket) {
    setEditingBucket(bucket);
    setBucketForm({ title: bucket.title || "", description: bucket.description || "", type: bucket.type || "TASK" });
    setShowBucketForm(true);
  }

  async function handleBucketSubmit(event) {
    event.preventDefault();
    if (!bucketForm.title.trim()) return;
    try {
      setBucketSaving(true); setError("");
      if (editingBucket) {
        const updated = await updateBucket(editingBucket.id, { title: bucketForm.title.trim(), description: bucketForm.description.trim() || null, type: bucketForm.type });
        setBuckets((current) => current.map((bucket) => bucket.id === editingBucket.id ? updated : bucket));
        setSelectedBucket(updated);
      } else {
        const created = await createBucket({ title: bucketForm.title.trim(), description: bucketForm.description.trim() || null, type: bucketForm.type, status: "OPEN" });
        setBuckets((current) => [created, ...current]);
      }
      setShowBucketForm(false); setEditingBucket(null); setBucketForm({ title: "", description: "", type: "TASK" });
    } catch (error) {
      console.error("Unable to save bucket:", error);
      setError(error?.message || "Unable to save bucket.");
    } finally { setBucketSaving(false); }
  }

  async function handleBucketStatus(bucket) {
    const nextStatus = bucket.status === "DONE" ? "OPEN" : "DONE";
    try {
      setError("");
      const updated = await updateBucket(bucket.id, { status: nextStatus });
      setBuckets((current) => current.map((item) => item.id === bucket.id ? updated : item));
      setSelectedBucket(updated);
    } catch (error) {
      console.error("Unable to update bucket:", error);
      setError(error?.message || "Unable to update bucket.");
    }
  }

  async function handleDeleteBucket(bucketId) {
    if (!window.confirm("Delete this bucket?")) return;
    try {
      await deleteBucket(bucketId);
      setBuckets((current) => current.filter((bucket) => bucket.id !== bucketId));
      setSelectedBucket(null);
    } catch (error) {
      console.error("Unable to delete bucket:", error);
      setError(error?.message || "Unable to delete bucket.");
    }
  }

  if (loading) return <div className="cf-page"><LoadingState label="Preparing your workspace..." /></div>;

  return (
    <div className="cf-page">
      <div className="cf-dashboard-top">
        <div>
          <div className="cf-eyebrow">Career workspace</div>
          <h1 className="cf-title">Welcome back, <span className="cf-accent">{userName}</span>.</h1>
          <p className="cf-muted cf-lead">Keep your professional profile, outreach and next actions in one focused workspace.</p>
        </div>
        <div className="cf-dashboard-meta">
          <span className="cf-status-dot" /> <span>Workspace active</span>
        </div>
      </div>

      {error && <div className="cf-alert">{error}</div>}

      <section className="cf-card cf-identity-card">
        <div className="cf-avatar">{initials(userName)}</div>
        <div className="cf-identity-main">
          <div className="cf-identity-name-row"><h2>{userName || "Your profile"}</h2><span className="cf-user-handle">@{username}</span></div>
          <div className="cf-identity-grid">
            <IdentityItem label="Username" value={username} />
            <IdentityItem label="Location" value={location} />
            <IdentityItem label="Professional email" value={professionalEmail} verified={emailConnected} />
          </div>
        </div>
      </section>

      <section className="cf-stat-grid">
        <StatCard label="Emails sent" value={emails.length} note="Professional outreach" icon={<MailIcon />} />
        <StatCard label="Open buckets" value={buckets.length - completedBuckets} note="Tasks still in progress" icon={<CheckIcon />} />
        <StatCard label="Completed" value={completedBuckets} note="Buckets marked done" icon={<SparkIcon />} />
      </section>

      <section className="cf-card cf-data-section">
        <SectionHeading eyebrow="Outreach" title="Professional emails" count={emails.length} action={emails.length > 4 ? () => setShowAllEmails((v) => !v) : null} actionText={showAllEmails ? "Show recent" : "View all"} />
        {sortedEmails.length === 0 ? <EmptyState title="No email records yet" text="Successful professional outreach will appear here automatically." /> : (
          <div className="cf-record-list">{(showAllEmails ? sortedEmails : sortedEmails.slice(0,4)).map((email, index) => <EmailRow key={email.id || index} email={email} onClick={() => setSelectedEmail(email)} />)}</div>
        )}
      </section>

      <section className="cf-card cf-data-section">
        <SectionHeading eyebrow="Your next actions" title="Buckets" count={`${completedBuckets}/${buckets.length}`} action={openAddBucket} actionText="Add bucket" />
        {sortedBuckets.length === 0 ? <EmptyState title="Your workspace is clear" text="Create a bucket for a task, reminder or follow-up you want to keep visible." action={openAddBucket} actionText="Create first bucket" /> : (
          <div className="cf-record-list">{(showAllBuckets ? sortedBuckets : sortedBuckets.slice(0,4)).map((bucket) => <BucketRow key={bucket.id} bucket={bucket} onOpen={() => setSelectedBucket(bucket)} onToggle={() => handleBucketStatus(bucket)} />)}</div>
        )}
        {sortedBuckets.length > 4 && <button type="button" className="cf-text-button cf-list-more" onClick={() => setShowAllBuckets((v) => !v)}>{showAllBuckets ? "Show recent buckets" : `View all ${sortedBuckets.length} buckets`}</button>}
      </section>

      {selectedEmail && <EmailModal email={selectedEmail} onClose={() => setSelectedEmail(null)} />}
      {selectedBucket && <BucketModal bucket={selectedBucket} onClose={() => setSelectedBucket(null)} onEdit={() => { openEditBucket(selectedBucket); setSelectedBucket(null); }} onToggle={() => handleBucketStatus(selectedBucket)} onDelete={() => handleDeleteBucket(selectedBucket.id)} />}
      {showBucketForm && <BucketFormModal form={bucketForm} setForm={setBucketForm} editing={editingBucket} saving={bucketSaving} onClose={() => setShowBucketForm(false)} onSubmit={handleBucketSubmit} />}
    </div>
  );
}

function IdentityItem({ label, value, verified }) {
  return <div><span className="cf-field-label">{label}</span><div className="cf-field-value">{value}{verified !== undefined && <span className={`cf-verified ${verified ? "yes" : "no"}`}>{verified ? "✓ Verified" : "○ Not verified"}</span>}</div></div>;
}
function StatCard({ label, value, note, icon }) { return <div className="cf-card cf-stat-card"><span className="cf-stat-icon">{icon}</span><strong>{value}</strong><span className="cf-stat-label">{label}</span><small>{note}</small></div>; }
function SectionHeading({ eyebrow, title, count, action, actionText }) { return <div className="cf-section-heading"><div><div className="cf-eyebrow">{eyebrow}</div><div className="cf-section-title-row"><h2 className="cf-section-title">{title}</h2>{count !== undefined && <span className="cf-count">{count}</span>}</div></div>{action && <button type="button" className="cf-button cf-button-secondary" onClick={action}>{actionText}</button>}</div>; }
function EmailRow({ email, onClick }) { const company = email.company_name || email.company || "Professional outreach"; const recipient = email.to_email || email.recipient_email || email.to || "Recipient unavailable"; return <button type="button" className="cf-record-row" onClick={onClick}><span className="cf-record-icon"><MailIcon /></span><span className="cf-record-main"><strong>{company}</strong><small>{recipient}</small></span><span className="cf-record-side"><span className="cf-success-dot">✓</span><small>{formatDate(email.sent_at || email.created_at)}</small></span><ChevronIcon /></button>; }
function BucketRow({ bucket, onOpen, onToggle }) { return <div className="cf-record-row bucket"><button type="button" className={`cf-check ${bucket.status === "DONE" ? "done" : ""}`} onClick={onToggle} aria-label="Toggle bucket status">{bucket.status === "DONE" ? "✓" : ""}</button><button type="button" className="cf-record-main cf-record-button" onClick={onOpen}><strong className={bucket.status === "DONE" ? "done-text" : ""}>{bucket.title}</strong><small>{bucket.description || bucket.type || "Task"}</small></button><span className={`cf-bucket-status ${bucket.status === "DONE" ? "done" : "open"}`}>{bucket.status === "DONE" ? "Done" : "Open"}</span><ChevronIcon /></div>; }
function EmailModal({ email, onClose }) {
  return (
    <Modal
      title="Email record"
      onClose={onClose}
    >
      <div className="cf-modal-grid">
        <Detail
          label="Company"
          value={
            email.company_name ||
            email.company
          }
        />

        <Detail
          label="HR email"
          value={
            email.to_email ||
            email.recipient_email ||
            email.to
          }
        />

        <Detail
          label="Role"
          value={
            email.role ||
            email.job_role
          }
        />

        <Detail
          label="Date"
          value={formatDate(
            email.sent_at ||
            email.created_at
          )}
        />
      </div>
    </Modal>
  );
}
function BucketModal({ bucket, onClose, onEdit, onToggle, onDelete }) { return <Modal title={bucket.title} onClose={onClose}><div className="cf-bucket-modal-head"><span className={`cf-bucket-status ${bucket.status === "DONE" ? "done" : "open"}`}>{bucket.status === "DONE" ? "Done" : "Open"}</span><span className="cf-muted">{bucket.type || "Task"}</span></div><Detail label="Description" value={bucket.description || "No description added."} large /><div className="cf-modal-actions"><button className="cf-button cf-button-secondary" onClick={onToggle}>{bucket.status === "DONE" ? "Mark open" : "Mark done"}</button><button className="cf-button cf-button-secondary" onClick={onEdit}>Edit</button><button className="cf-button cf-danger" onClick={onDelete}>Delete</button></div></Modal>; }
function BucketFormModal({ form, setForm, editing, saving, onClose, onSubmit }) { return <Modal title={editing ? "Edit bucket" : "New bucket"} onClose={onClose}><form onSubmit={onSubmit} className="cf-form"><label>Title<input value={form.title} onChange={(e) => setForm((v) => ({ ...v, title: e.target.value }))} placeholder="e.g. Follow up with recruiter" autoFocus /></label><label>Description<textarea value={form.description} onChange={(e) => setForm((v) => ({ ...v, description: e.target.value }))} placeholder="Add useful context..." rows={4} /></label><label>Type<select value={form.type} onChange={(e) => setForm((v) => ({ ...v, type: e.target.value }))}><option value="TASK">Task</option><option value="REMINDER">Reminder</option><option value="FOLLOW_UP">Follow up</option></select></label><div className="cf-modal-actions"><button type="button" className="cf-button cf-button-secondary" onClick={onClose}>Cancel</button><button type="submit" className="cf-button cf-button-primary" disabled={saving}>{saving ? "Saving..." : editing ? "Save changes" : "Create bucket"}</button></div></form></Modal>; }
function Modal({ title, onClose, children }) { return <div className="cf-modal-backdrop" onMouseDown={onClose}><div className="cf-modal" onMouseDown={(e) => e.stopPropagation()}><header><div><div className="cf-eyebrow">CareerForge</div><h3>{title}</h3></div><button type="button" className="cf-modal-close" onClick={onClose}>×</button></header><div className="cf-modal-body">{children}</div></div></div>; }
function Detail({ label, value, large }) { return <div className={large ? "cf-detail cf-detail-large" : "cf-detail"}><span>{label}</span><p>{value || "Not available"}</p></div>; }
function EmptyState({ title, text, action, actionText }) { return <div className="cf-empty-state"><div className="cf-empty-icon"><SparkIcon /></div><strong>{title}</strong><span>{text}</span>{action && <button type="button" className="cf-button cf-button-secondary" onClick={action}>{actionText}</button>}</div>; }
function LoadingState({ label }) { return <div className="cf-loading"><span className="cf-spinner" />{label}</div>; }
function initials(name) { return (name || "CF").split(" ").filter(Boolean).slice(0,2).map((part) => part[0]).join("").toUpperCase(); }
function formatDate(value) { if (!value) return ""; const date = new Date(value); return Number.isNaN(date.getTime()) ? "" : date.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" }); }
function MailIcon() { return <svg viewBox="0 0 24 24" fill="none"><rect x="3" y="5" width="18" height="14" rx="2" stroke="currentColor" strokeWidth="1.8"/><path d="m4 7 8 6 8-6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/></svg>; }
function CheckIcon() { return <svg viewBox="0 0 24 24" fill="none"><path d="M7 4h10v16H7z" stroke="currentColor" strokeWidth="1.8"/><path d="m9 12 2 2 4-4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/></svg>; }
function SparkIcon() { return <svg viewBox="0 0 24 24" fill="none"><path d="m12 3 1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7L12 3Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round"/></svg>; }
function ChevronIcon() { return <svg className="cf-chevron" viewBox="0 0 24 24" fill="none"><path d="m9 18 6-6-6-6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/></svg>; }
