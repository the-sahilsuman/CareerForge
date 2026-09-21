import { Link } from "react-router-dom";

export default function About() {
  return (
    <div className="cf-page">
      <section className="cf-about-hero cf-card">
        <div className="cf-about-mark"><LogoMark /></div>
        <div>
          <div className="cf-eyebrow">About CareerForge</div>
          <h1 className="cf-title">A practical career workspace, built around you.</h1>
          <p className="cf-about-lead">CareerForge brings your professional profile, resume, outreach records, tasks and AI career assistance together in one place — without making the workflow feel complicated.</p>
        </div>
      </section>

      <section className="cf-about-grid">
        <AboutCard number="01" title="Your professional profile" text="Keep your personal details, bio, experience, certifications, projects, skills and professional links organised in one profile." />
        <AboutCard number="02" title="Application support" text="Use your resume and career context with the assistant to understand roles, prepare applications and work through next steps." />
        <AboutCard number="03" title="Professional outreach" text="CareerForge keeps successful outreach records and your professional email workflow connected to the same workspace." />
        <AboutCard number="04" title="Simple task management" text="Buckets give you a lightweight place for follow-ups, reminders and career tasks, with clear Open and Done states." />
      </section>

      <section className="cf-card cf-about-builder">
        <div>
          <div className="cf-eyebrow">Built as a focused project</div>
          <h2>Designed to be useful before it is complicated.</h2>
          <p>CareerForge is intentionally kept focused: a clean frontend, a protected backend, an AI assistant and the practical data needed to support a modern job-search workflow.</p>
        </div>
        <div className="cf-about-stack"><span>React</span><span>FastAPI</span><span>AWS</span><span>AI / RAG</span><span>PostgreSQL</span></div>
      </section>

      <section className="cf-card cf-about-me">
        <div className="cf-eyebrow">About the builder</div>
        <h2>Built with an engineering-first mindset.</h2>
        <p>CareerForge is built by Sahil Suman as a hands-on full-stack and cloud engineering project, combining React, FastAPI, AWS, DevOps practices and an agentic AI workflow into one practical product.</p>
        <Link className="cf-button cf-button-primary" to="/profile">View professional profile</Link>
      </section>
    </div>
  );
}
function AboutCard({ number, title, text }) { return <article className="cf-card cf-about-card"><span>{number}</span><h2>{title}</h2><p>{text}</p></article>; }
function LogoMark() { return <svg viewBox="0 0 32 32" fill="none"><path d="M7 23.5 13.5 17l4.5 4.5L25 14.5" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round"/><path d="M7 23.5V9h18v5.5" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round"/><circle cx="13.5" cy="17" r="2" fill="currentColor"/><circle cx="25" cy="14.5" r="2" fill="currentColor"/></svg>; }
