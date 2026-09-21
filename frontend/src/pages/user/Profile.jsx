import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../auth/AuthProvider";
import { getProfile } from "../../services/api/profileApi";
import { getSkills } from "../../services/api/skillApi";
import { getProjects } from "../../services/api/projectApi";
import { getCertifications } from "../../services/api/certificationApi";
import { getExperience } from "../../services/api/experienceApi";
import { getResumes } from "../../services/api/resumeApi";
// import { getEmailConnections } from "../../services/api/emailConnectionApi";
import { getEmailConnections,getGoogleAuthorizationUrl, disconnectEmailConnection } from "../../services/api/emailConnectionApi";

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [skills, setSkills] = useState([]);
  const [projects, setProjects] = useState([]);
  const [experience, setExperience] = useState([]);
  const [certifications, setCertifications] = useState([]);
  const [resumes, setResumes] = useState([]);
  const [emailConnection, setEmailConnection] = useState(null);
  const [connectionBusy, setConnectionBusy] = useState(false);
  const [connectionError, setConnectionError] = useState("");
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState(null);

  const { user, backendUser } = useAuth();

  useEffect(() => { loadProfile(); }, []);

  async function loadProfile() {
    setLoading(true);
    const results = await Promise.allSettled([
      getProfile(), getSkills(), getProjects(), getExperience(), getCertifications(), getResumes(), getEmailConnections(),
    ]);
    if (results[0].status === "fulfilled") setProfile(results[0].value);
    if (results[1].status === "fulfilled") setSkills(normalizeArray(results[1].value));
    if (results[2].status === "fulfilled") setProjects(normalizeArray(results[2].value));
    if (results[3].status === "fulfilled") setExperience(normalizeArray(results[3].value));
    if (results[4].status === "fulfilled") setCertifications(normalizeArray(results[4].value));
    if (results[5].status === "fulfilled") setResumes(normalizeResumes(results[5].value));
    if (results[6].status === "fulfilled") {
      const connections = Array.isArray(results[6].value) ? results[6].value : [];
      setEmailConnection(connections[0] || null);
    }
    setLoading(false);
  }

  const fullName = [profile?.first_name, profile?.last_name].filter(Boolean).join(" ") || "Your Name";
  const resume = resumes[0];
  const sortedExperience = useMemo(() => sortLatest(experience), [experience]);
  const sortedProjects = useMemo(() => sortLatest(projects), [projects]);
  const sortedCertifications = useMemo(() => sortLatest(certifications), [certifications]);
  const professionalEmail = profile?.professional_email || "Not configured";
  const username = backendUser?.user_id || user?.username || "—";

  if (loading) return <div className="cf-page"><div className="cf-loading"><span className="cf-spinner" />Loading your profile...</div></div>;

  return (
    <div className="cf-page">
      <header className="cf-profile-header cf-card">
        <div className="cf-profile-heading">
          <div className="cf-avatar">{initials(fullName)}</div>
          <div>
            <div className="cf-eyebrow">Professional profile</div>
            <h1 className="cf-title">{fullName}</h1>
            <p className="cf-muted">{profile?.location || "Add your location to make your profile complete."}</p>
          </div>
        </div>
        <div className="cf-profile-actions">
          <button
            type="button"
            className={`cf-button ${
              emailConnection
                ? "cf-button-danger"
                : "cf-button-secondary"
            }`}
            disabled={connectionBusy}
            onClick={async () => {
              setConnectionError("");
              setConnectionBusy(true);

              try {
                if (emailConnection?.id) {
                  const confirmed = window.confirm(
                    "Disconnect your professional Gmail connection?"
                  );

                  if (!confirmed) return;

                  await disconnectEmailConnection(
                    emailConnection.id
                  );

                  setEmailConnection(null);
                } else {
                  const result =
                    await getGoogleAuthorizationUrl();

                  const authorizationUrl =
                    result?.authorization_url;

                  if (!authorizationUrl) {
                    throw new Error(
                      "Unable to start Google email connection."
                    );
                  }

                  window.location.assign(
                    authorizationUrl
                  );
                }
              } catch (error) {
                console.error(
                  "Unable to update email connection:",
                  error
                );

                setConnectionError(
                  error?.message ||
                    "Unable to update professional email connection."
                );
              } finally {
                setConnectionBusy(false);
              }
            }}
          >
            {connectionBusy
              ? "Working..."
              : emailConnection
                ? "Revoke Email"
                : "Connect Email"}
          </button>
          {resume?.object_url && <a className="cf-button cf-button-secondary" href={resume.object_url} target="_blank" rel="noreferrer"><PdfIcon /> View Resume</a>}
          <Link className="cf-button cf-button-primary" to="/profile/edit"><EditIcon /> Edit Profile</Link>
        </div>
      </header>

      <section className="cf-profile-info-grid">
        <InfoCard label="Mobile" value={profile?.phone} />
        <InfoCard label="UserID" value={username} />
        <InfoCard label="Professional email" value={professionalEmail} verified={!!emailConnection} />
        <InfoCard label="Location" value={profile?.location} />
      </section>

      <section className="cf-card cf-profile-section">
        <SectionTitle eyebrow="About Me" title="Professional bio" />
        <p className="cf-bio">{profile?.bio || "No professional bio has been added yet. Use Edit profile to introduce your experience, strengths and direction."}</p>
      </section>

      {(profile?.linkedin_url || profile?.github_url || profile?.portfolio_url) && (
        <section className="cf-card cf-profile-section">
          <SectionTitle eyebrow="Online presence" title="Professional links" />
          <div className="cf-link-grid">
            {profile?.linkedin_url && <ExternalLink label="LinkedIn" value={profile.linkedin_url} />}
            {profile?.github_url && <ExternalLink label="GitHub" value={profile.github_url} />}
            {profile?.portfolio_url && <ExternalLink label="Portfolio" value={profile.portfolio_url} />}
          </div>
        </section>
      )}

      <ProfileCollection title="Experience" eyebrow="Career history" items={sortedExperience} empty="No experience added yet." onSelect={(item) => setSelectedItem({ type: "experience", item })} render={experienceSummary} />
      <ProfileCollection title="Certifications" eyebrow="Credentials" items={sortedCertifications} empty="No certifications added yet." onSelect={(item) => setSelectedItem({ type: "certification", item })} render={certificationSummary} />
      <ProfileCollection title="Projects" eyebrow="Selected work" items={sortedProjects} empty="No projects added yet." onSelect={(item) => setSelectedItem({ type: "project", item })} render={projectSummary} />

      {skills.length > 0 && (
        <section className="cf-card cf-profile-section">
          <SectionTitle eyebrow="Capabilities" title={`Skills · ${skills.length}`} />
          <div className="cf-skill-list">{skills.map((skill) => <span className="cf-skill-chip" key={skill.id || skill.name}>{skill.name}{skill.proficiency ? <small>{skill.proficiency}</small> : null}</span>)}</div>
        </section>
      )}

      {selectedItem && <ProfileItemModal type={selectedItem.type} item={selectedItem.item} onClose={() => setSelectedItem(null)} />}
    </div>
  );
}

function ProfileCollection({ title, eyebrow, items, empty, onSelect, render }) {
  return <section className="cf-card cf-profile-section"><SectionTitle eyebrow={eyebrow} title={title} count={items.length} />{items.length === 0 ? <p className="cf-empty-inline">{empty}</p> : <div className="cf-horizontal-list">{items.map((item, index) => <button type="button" className="cf-profile-row" key={item.id || index} onClick={() => onSelect(item)}>{render(item)}<ChevronIcon /></button>)}</div>}</section>;
}
function experienceSummary(item) { return <><span className="cf-collection-icon"><BriefcaseIcon /></span><span className="cf-collection-main"><strong>{item.title || item.role || item.position || "Experience"}</strong><small>{item.company || item.company_name || "Company not added"}</small></span><span className="cf-collection-date">{formatDate(item.updated_at || item.created_at || item.start_date)}</span></>; }
function certificationSummary(item) { return <><span className="cf-collection-icon"><BadgeIcon /></span><span className="cf-collection-main"><strong>{item.name || item.title || "Certification"}</strong><small>{item.issuer || item.organization || "Issuer not added"}</small></span><span className="cf-collection-date">{formatDate(item.updated_at || item.created_at || item.issue_date)}</span></>; }
function projectSummary(item) { return <><span className="cf-collection-icon"><CodeIcon /></span><span className="cf-collection-main"><strong>{item.name || item.title || "Project"}</strong><small>{item.description || item.technologies || "Project details available"}</small></span><span className="cf-collection-date">{formatDate(item.updated_at || item.created_at)}</span></>; }
function ProfileItemModal({ type, item, onClose }) {
  const title = type === "experience" ? (item.title || item.role || item.position || "Experience") : type === "certification" ? (item.name || item.title || "Certification") : (item.name || item.title || "Project");
  return <div className="cf-modal-backdrop" onMouseDown={onClose}><div className="cf-modal" onMouseDown={(e) => e.stopPropagation()}><header><div><div className="cf-eyebrow">{type}</div><h3>{title}</h3></div><button className="cf-modal-close" onClick={onClose}>×</button></header><div className="cf-modal-body"><DynamicDetails type={type} item={item} /></div></div></div>;
}
function DynamicDetails({ type, item }) {
  const hidden = new Set(["id", "user_id", "profile_id"]);
  const preferred = type === "experience" ? ["company", "company_name", "location", "start_date", "end_date", "description", "employment_type"] : type === "certification" ? ["issuer", "organization", "credential_id", "credential_url", "issue_date", "expiry_date", "description"] : ["description", "technologies", "project_url", "github_url", "start_date", "end_date"];
  const keys = [...preferred, ...Object.keys(item || {})].filter((key, index, arr) => !hidden.has(key) && arr.indexOf(key) === index && item[key] !== null && item[key] !== "");
  return <div className="cf-detail-stack">{keys.map((key) => <Detail key={key} label={prettyLabel(key)} value={item[key]} link={key.endsWith("_url")} />)}</div>;
}
function InfoCard({ label, value, verified }) { return <div className="cf-card cf-info-card"><span>{label}</span><strong>{value || "Not added"}</strong>{verified !== undefined && <small className={verified ? "verified" : ""}>{verified ? "✓ Verified connection" : "○ Not verified"}</small>}</div>; }
function SectionTitle({ eyebrow, title, count }) { return <div className="cf-section-heading"><div><div className="cf-eyebrow">{eyebrow}</div><div className="cf-section-title-row"><h2 className="cf-section-title">{title}</h2>{count !== undefined && <span className="cf-count">{count}</span>}</div></div></div>; }
function ExternalLink({ label, value }) { return <a className="cf-link-card" href={value} target="_blank" rel="noreferrer"><span>{label}</span><strong>{value}</strong><ChevronIcon /></a>; }
function Detail({ label, value, link }) { return <div className="cf-detail"><span>{prettyLabel(label)}</span>{link && typeof value === "string" ? <a href={value} target="_blank" rel="noreferrer">{value}</a> : <p>{typeof value === "object" ? JSON.stringify(value, null, 2) : String(value)}</p>}</div>; }
function prettyLabel(value) { return String(value).replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase()); }
function sortLatest(items) { return [...items].sort((a,b) => new Date(b.updated_at || b.modified_at || b.created_at || b.issue_date || b.start_date || 0) - new Date(a.updated_at || a.modified_at || a.created_at || a.issue_date || a.start_date || 0)); }
function normalizeArray(data) { if (Array.isArray(data)) return data; if (Array.isArray(data?.items)) return data.items; if (Array.isArray(data?.data)) return data.data; return []; }
function normalizeResumes(data) { if (!data) return []; if (!Array.isArray(data) && typeof data === "object" && (data.id || data.file_name || data.object_url || data.s3_key)) return [data]; if (Array.isArray(data)) return data.filter(Boolean); if (data.data) return normalizeResumes(data.data); if (Array.isArray(data.items)) return data.items.filter(Boolean); if (Array.isArray(data.resumes)) return data.resumes.filter(Boolean); return []; }
function initials(name) { return (name || "CF").split(" ").filter(Boolean).slice(0,2).map((part) => part[0]).join("").toUpperCase(); }
function formatDate(value) { if (!value) return ""; const d = new Date(value); return Number.isNaN(d.getTime()) ? "" : d.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" }); }
function ChevronIcon() { return <svg className="cf-chevron" viewBox="0 0 24 24" fill="none"><path d="m9 18 6-6-6-6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/></svg>; }
function PdfIcon() { return <svg viewBox="0 0 24 24" fill="none"><path d="M6 3h8l4 4v14H6z" stroke="currentColor" strokeWidth="1.7"/><path d="M14 3v5h5M8.5 16h2M8.5 12h7" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round"/></svg>; }
function EditIcon() { return <svg viewBox="0 0 24 24" fill="none"><path d="m14 6 4 4M4 20l4.5-1 10-10a2.1 2.1 0 0 0-3-3l-10 10L4 20Z" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/></svg>; }
function BriefcaseIcon() { return <svg viewBox="0 0 24 24" fill="none"><rect x="3" y="7" width="18" height="13" rx="2" stroke="currentColor" strokeWidth="1.8"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" stroke="currentColor" strokeWidth="1.8"/></svg>; }
function BadgeIcon() { return <svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="9" r="5" stroke="currentColor" strokeWidth="1.8"/><path d="m9 13-1 7 4-2 4 2-1-7" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round"/></svg>; }
function CodeIcon() { return <svg viewBox="0 0 24 24" fill="none"><path d="m9 8-4 4 4 4M15 8l4 4-4 4M13 5l-2 14" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/></svg>; }
