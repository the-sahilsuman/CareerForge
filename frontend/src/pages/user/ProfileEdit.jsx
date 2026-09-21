import {
  useEffect,
  useRef,
  useState,
} from "react";

import { Link } from "react-router-dom";

import {
  getProfile,
  createProfile,
  updateProfile,
} from "../../services/api/profileApi";

import {
  getSkills,
  createSkill,
  updateSkill,
  deleteSkill,
} from "../../services/api/skillApi";

import {
  getProjects,
  createProject,
  updateProject,
  deleteProject,
} from "../../services/api/projectApi";

import {
  getExperience,
  createExperience,
  updateExperience,
  deleteExperience,
} from "../../services/api/experienceApi";

import {
  getCertifications,
  createCertification,
  updateCertification,
  deleteCertification,
} from "../../services/api/certificationApi";

import apiClient from "../../services/api/client";

/*
|--------------------------------------------------------------------------
| Profile sections
|--------------------------------------------------------------------------
*/

const SECTIONS = [
  {
    id: "personal",
    title: "Personal Information",
    description: "Name, phone and location",
  },
  {
    id: "bio",
    title: "Bio",
    description: "Your professional introduction",
  },
  {
    id: "email",
    title: "Professional Email",
    description:
      "Email used for professional communication",
  },
  {
    id: "links",
    title: "Professional Links",
    description:
      "LinkedIn, GitHub and portfolio",
  },
  {
    id: "resume",
    title: "Resume",
    description:
      "Upload, view or delete your resume",
  },
  {
    id: "skills",
    title: "Skills",
    description:
      "Technical and professional skills",
  },
  {
    id: "certifications",
    title: "Certifications",
    description:
      "Professional certifications and credentials",
  },
  {
    id: "projects",
    title: "Projects",
    description:
      "Projects and technologies",
  },
  {
    id: "experience",
    title: "Experience",
    description:
      "Work and internship experience",
  },
];

const EMPTY_PROFILE = {
  first_name: "",
  last_name: "",
  phone: "",
  location: "",
  bio: "",
  linkedin_url: "",
  github_url: "",
  portfolio_url: "",
  professional_email: "",
};

/*
|--------------------------------------------------------------------------
| Main component
|--------------------------------------------------------------------------
*/

export default function ProfileEdit() {
  const [selected, setSelected] =
    useState("personal");

  const [profile, setProfile] =
    useState(EMPTY_PROFILE);

  const [profileExists, setProfileExists] =
    useState(false);

  const [skills, setSkills] =
    useState([]);

  const [projects, setProjects] =
    useState([]);

  const [experience, setExperience] =
    useState([]);

  const [certifications, setCertifications] =
    useState([]);

  const [resumes, setResumes] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [message, setMessage] =
    useState("");

  const [error, setError] =
    useState("");

  /*
  |--------------------------------------------------------------------------
  | Load everything
  |--------------------------------------------------------------------------
  */

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      setError("");

      /*
       * Resume failure must NOT prevent profile,
       * skills, projects or experience from loading.
       *
       * No resume is valid:
       * GET /api/v1/resumes -> []
       */

      const [
        profileData,
        skillsData,
        projectsData,
        experienceData,
        certificationsData,
        resumesData,
      ] = await Promise.all([
        getProfile().catch(() => null),

        getSkills().catch(() => []),

        getProjects().catch(() => []),

        getExperience().catch(() => []),

        getCertifications().catch(() => []),

        apiClient
          .get("/api/v1/resumes")
          .catch((resumeError) => {
            console.error(
              "Unable to load resumes:",
              resumeError
            );

            return [];
          }),
      ]);

      /*
      |--------------------------------------------------------------------------
      | Profile
      |--------------------------------------------------------------------------
      */

      if (profileData) {
        setProfile({
          first_name:
            profileData.first_name ?? "",

          last_name:
            profileData.last_name ?? "",

          phone:
            profileData.phone ?? "",

          location:
            profileData.location ?? "",

          bio:
            profileData.bio ?? "",

          linkedin_url:
            profileData.linkedin_url ?? "",

          github_url:
            profileData.github_url ?? "",

          portfolio_url:
            profileData.portfolio_url ?? "",

          professional_email:
            profileData.professional_email ?? "",
        });

        setProfileExists(true);
      } else {
        setProfile(EMPTY_PROFILE);
        setProfileExists(false);
      }

      /*
      |--------------------------------------------------------------------------
      | Other profile data
      |--------------------------------------------------------------------------
      */

      setSkills(
        Array.isArray(skillsData)
          ? skillsData
          : []
      );

      setProjects(
        Array.isArray(projectsData)
          ? projectsData
          : []
      );

      setExperience(
        Array.isArray(experienceData)
          ? experienceData
          : []
      );

      setCertifications(
        Array.isArray(certificationsData)
          ? certificationsData
          : []
      );

      /*
      |--------------------------------------------------------------------------
      | Resume
      |--------------------------------------------------------------------------
      |
      | Existing RDS rows arrive here.
      |
      | If no row exists:
      |
      | resumes = []
      |
      | That is completely valid.
      |--------------------------------------------------------------------------
      */

      setResumes(
        Array.isArray(resumesData)
          ? resumesData
          : []
      );
    } catch (err) {
      console.error(
        "Unable to load profile editor:",
        err
      );

      setError(
        err?.message ||
          "Unable to load profile."
      );
    } finally {
      setLoading(false);
    }
  }

  /*
  |--------------------------------------------------------------------------
  | Save profile
  |--------------------------------------------------------------------------
  */

  async function saveProfile(event) {
    event.preventDefault();

    try {
      setSaving(true);
      setMessage("");
      setError("");

      const payload = {
        first_name:
          profile.first_name.trim(),

        last_name:
          profile.last_name.trim() || null,

        phone:
          profile.phone.trim() || null,

        location:
          profile.location.trim() || null,

        bio:
          profile.bio.trim() || null,

        linkedin_url:
          profile.linkedin_url.trim() || null,

        github_url:
          profile.github_url.trim() || null,

        portfolio_url:
          profile.portfolio_url.trim() || null,

        professional_email:
          profile.professional_email.trim() ||
          null,
      };

      if (profileExists) {
        const updated =
          await updateProfile(payload);

        if (updated) {
          setProfile((current) => ({
            ...current,
            ...updated,
          }));
        }

        setMessage(
          "Profile updated successfully."
        );
      } else {
        const created =
          await createProfile(payload);

        if (created) {
          setProfile({
            first_name:
              created.first_name ?? "",

            last_name:
              created.last_name ?? "",

            phone:
              created.phone ?? "",

            location:
              created.location ?? "",

            bio:
              created.bio ?? "",

            linkedin_url:
              created.linkedin_url ?? "",

            github_url:
              created.github_url ?? "",

            portfolio_url:
              created.portfolio_url ?? "",

            professional_email:
              created.professional_email ?? "",
          });
        }

        setProfileExists(true);

        setMessage(
          "Profile created successfully."
        );
      }
    } catch (err) {
      console.error(
        "Unable to save profile:",
        err
      );

      setError(
        err?.message ||
          "Unable to save profile."
      );
    } finally {
      setSaving(false);
    }
  }

  /*
  |--------------------------------------------------------------------------
  | Loading
  |--------------------------------------------------------------------------
  */

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 p-8 text-slate-400">
        Loading profile editor...
      </div>
    );
  }

  /*
  |--------------------------------------------------------------------------
  | UI
  |--------------------------------------------------------------------------
  */

  return (
    <div className="min-h-screen bg-slate-950 p-8 text-white">
      <div className="mx-auto max-w-7xl">

        {/* Header */}

        <div className="mb-8 flex flex-col justify-between gap-5 md:flex-row md:items-center">

          <div>
            <p className="text-sm text-slate-500">
              Profile Editor
            </p>

            <h1 className="mt-2 text-3xl font-bold">
              Edit Profile
            </h1>

            <p className="mt-2 text-slate-400">
              Manage every part of your professional
              profile.
            </p>
          </div>

          <Link
            to="/profile"
            className="rounded-lg border border-slate-700 px-5 py-3 text-center text-sm font-semibold transition hover:bg-slate-900"
          >
            ← View Profile
          </Link>
        </div>

        {/* Global messages */}

        {error && (
          <div className="mb-6 rounded-xl border border-red-800 bg-red-950/40 px-5 py-4 text-sm text-red-300">
            {error}
          </div>
        )}

        {message && (
          <div className="mb-6 rounded-xl border border-green-800 bg-green-950/40 px-5 py-4 text-sm text-green-300">
            {message}
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-[280px_1fr]">

          {/* Sidebar */}

          <aside className="h-fit rounded-2xl border border-slate-800 bg-slate-900 p-3">

            {SECTIONS.map((section) => (
              <button
                key={section.id}
                type="button"
                onClick={() => {
                  setSelected(section.id);
                  setMessage("");
                  setError("");
                }}
                className={`mb-1 w-full rounded-xl p-4 text-left transition ${
                  selected === section.id
                    ? "bg-blue-600 text-white"
                    : "text-slate-400 hover:bg-slate-800 hover:text-white"
                }`}
              >
                <p className="font-semibold">
                  {section.title}
                </p>

                <p
                  className={`mt-1 text-xs ${
                    selected === section.id
                      ? "text-blue-100"
                      : "text-slate-600"
                  }`}
                >
                  {section.description}
                </p>
              </button>
            ))}
          </aside>

          {/* Main content */}

          <main className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

            {selected === "personal" && (
              <PersonalSection
                profile={profile}
                setProfile={setProfile}
                saveProfile={saveProfile}
                saving={saving}
              />
            )}

            {selected === "bio" && (
              <BioSection
                profile={profile}
                setProfile={setProfile}
                saveProfile={saveProfile}
                saving={saving}
              />
            )}

            {selected === "email" && (
              <EmailSection
                profile={profile}
                setProfile={setProfile}
                saveProfile={saveProfile}
                saving={saving}
              />
            )}

            {selected === "links" && (
              <LinksSection
                profile={profile}
                setProfile={setProfile}
                saveProfile={saveProfile}
                saving={saving}
              />
            )}

            {selected === "resume" && (
              <ResumeSection
                resumes={resumes}
                setResumes={setResumes}
              />
            )}

            {selected === "skills" && (
              <SkillsSection
                skills={skills}
                setSkills={setSkills}
              />
            )}

            {selected === "certifications" && (
              <CertificationSection
                certifications={certifications}
                setCertifications={setCertifications}
              />
            )}

            {selected === "projects" && (
              <ProjectsSection
                projects={projects}
                setProjects={setProjects}
              />
            )}

            {selected === "experience" && (
              <ExperienceSection
                experience={experience}
                setExperience={setExperience}
              />
            )}
          </main>
        </div>
      </div>

    </div>
  );
}

/*
|--------------------------------------------------------------------------
| Personal
|--------------------------------------------------------------------------
*/

function PersonalSection({
  profile,
  setProfile,
  saveProfile,
  saving,
}) {
  return (
    <form
      onSubmit={saveProfile}
      className="space-y-6"
    >
      <SectionHeader
        title="Personal Information"
        description="Basic information about you."
      />

      <div className="grid gap-5 md:grid-cols-2">

        <Input
          label="First Name"
          value={profile.first_name}
          onChange={(value) =>
            setProfile({
              ...profile,
              first_name: value,
            })
          }
          required
        />

        <Input
          label="Last Name"
          value={profile.last_name}
          onChange={(value) =>
            setProfile({
              ...profile,
              last_name: value,
            })
          }
        />

        <Input
          label="Phone"
          value={profile.phone}
          onChange={(value) =>
            setProfile({
              ...profile,
              phone: value,
            })
          }
        />

        <Input
          label="Location"
          value={profile.location}
          onChange={(value) =>
            setProfile({
              ...profile,
              location: value,
            })
          }
        />
      </div>

      <SaveButton saving={saving} />
    </form>
  );
}

/*
|--------------------------------------------------------------------------
| Bio
|--------------------------------------------------------------------------
*/

function BioSection({
  profile,
  setProfile,
  saveProfile,
  saving,
}) {
  return (
    <form
      onSubmit={saveProfile}
      className="space-y-6"
    >
      <SectionHeader
        title="Bio"
        description="Tell recruiters who you are."
      />

      <textarea
        value={profile.bio}
        onChange={(event) =>
          setProfile({
            ...profile,
            bio: event.target.value,
          })
        }
        maxLength={2500}
        rows={10}
        placeholder="Write your professional bio..."
        className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-blue-500"
      />

      <p className="text-xs text-slate-600">
        {profile.bio.length}/2500 characters
      </p>

      <SaveButton saving={saving} />
    </form>
  );
}

/*
|--------------------------------------------------------------------------
| Professional email
|--------------------------------------------------------------------------
*/

function EmailSection({
  profile,
  setProfile,
  saveProfile,
  saving,
}) {
  return (
    <form
      onSubmit={saveProfile}
      className="space-y-6"
    >
      <SectionHeader
        title="Professional Email"
        description="Your professional communication email."
      />

      <Input
        label="Professional Email"
        type="email"
        value={profile.professional_email}
        onChange={(value) =>
          setProfile({
            ...profile,
            professional_email: value,
          })
        }
        placeholder="you@example.com"
      />

      <p className="text-sm text-slate-500">
        Changing your professional email will disconnect
        the current Gmail connection. You will need to
        connect Gmail again using the new email address.
      </p>

      <SaveButton saving={saving} />
    </form>
  );
}

/*
|--------------------------------------------------------------------------
| Links
|--------------------------------------------------------------------------
*/

function LinksSection({
  profile,
  setProfile,
  saveProfile,
  saving,
}) {
  return (
    <form
      onSubmit={saveProfile}
      className="space-y-6"
    >
      <SectionHeader
        title="Professional Links"
        description="Connect your professional presence."
      />

      <Input
        label="LinkedIn"
        type="url"
        value={profile.linkedin_url}
        onChange={(value) =>
          setProfile({
            ...profile,
            linkedin_url: value,
          })
        }
        placeholder="https://linkedin.com/in/..."
      />

      <Input
        label="GitHub"
        type="url"
        value={profile.github_url}
        onChange={(value) =>
          setProfile({
            ...profile,
            github_url: value,
          })
        }
        placeholder="https://github.com/..."
      />

      <Input
        label="Portfolio"
        type="url"
        value={profile.portfolio_url}
        onChange={(value) =>
          setProfile({
            ...profile,
            portfolio_url: value,
          })
        }
        placeholder="https://..."
      />

      <SaveButton saving={saving} />
    </form>
  );
}

/*
|--------------------------------------------------------------------------
| RESUME
|--------------------------------------------------------------------------
*/

function ResumeSection({
  resumes,
  setResumes,
}) {
  const inputRef = useRef(null);

  const [uploading, setUploading] =
    useState(false);

  const [progress, setProgress] =
    useState(0);

  const [resumeError, setResumeError] =
    useState("");

  const [resumeMessage, setResumeMessage] =
    useState("");

  /*
  |--------------------------------------------------------------------------
  | Upload
  |--------------------------------------------------------------------------
  */

  async function handleUpload(event) {
    const file =
      event.target.files?.[0];

    /*
     * Reset input so selecting the same file
     * again still triggers onChange.
     */
    event.target.value = "";

    if (!file) {
      return;
    }

    setResumeError("");
    setResumeMessage("");
    setProgress(0);

    /*
    |--------------------------------------------------------------------------
    | Validation
    |--------------------------------------------------------------------------
    */

    const allowedTypes = [
      "application/pdf",
      "application/msword",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];

    const allowedExtensions = [
      ".pdf",
      ".doc",
      ".docx",
    ];

    const lowerName =
      file.name.toLowerCase();

    const validType =
      allowedTypes.includes(file.type);

    const validExtension =
      allowedExtensions.some(
        (extension) =>
          lowerName.endsWith(extension)
      );

    if (
      !validType &&
      !validExtension
    ) {
      setResumeError(
        "Please upload a PDF, DOC or DOCX resume."
      );

      return;
    }

    /*
     * 10 MB frontend safety limit.
     */
    if (
      file.size >
      10 * 1024 * 1024
    ) {
      setResumeError(
        "Resume must be smaller than 10 MB."
      );

      return;
    }

    /*
    |--------------------------------------------------------------------------
    | FormData
    |--------------------------------------------------------------------------
    */

    const formData = new FormData();

    /*
     * THIS NAME MUST BE "file"
     *
     * Backend:
     *
     * file: UploadFile = File(...)
     */
    formData.append(
      "file",
      file
    );

    try {
      setUploading(true);

      /*
      |--------------------------------------------------------------------------
      | IMPORTANT
      |--------------------------------------------------------------------------
      |
      | Do NOT manually set:
      |
      | Content-Type: multipart/form-data
      |
      | apiClient.upload() intentionally lets
      | the browser generate the multipart boundary.
      |--------------------------------------------------------------------------
      */

      const uploaded =
        await apiClient.upload(
          "/api/v1/resumes/upload",
          formData,
          (percentage) => {
            setProgress(percentage);
          }
        );

      /*
      |--------------------------------------------------------------------------
      | Backend returns the new Resume row.
      |--------------------------------------------------------------------------
      */

      if (uploaded) {
        /*
         * User wants one current resume.
         *
         * The backend currently returns the created
         * resume row. We place it at the beginning.
         *
         * If an older row exists, keep it visible because
         * the backend GET endpoint can return multiple rows.
         */
        setResumes((current) => {
          const withoutUploaded =
            current.filter(
              (resume) =>
                resume.id !== uploaded.id
            );

          return [
            uploaded,
            ...withoutUploaded,
          ];
        });
      }

      setResumeMessage(
        "Resume uploaded successfully."
      );
    } catch (err) {
      console.error(
        "Resume upload failed:",
        err
      );

      setResumeError(
        err?.message ||
          "Unable to upload resume."
      );
    } finally {
      setUploading(false);
      setProgress(0);
    }
  }

  /*
  |--------------------------------------------------------------------------
  | Delete
  |--------------------------------------------------------------------------
  */

  async function handleDelete(
    resumeId
  ) {
    if (!resumeId) {
      return;
    }

    const confirmed =
      window.confirm(
        "Delete this resume?"
      );

    if (!confirmed) {
      return;
    }

    try {
      setResumeError("");
      setResumeMessage("");

      await apiClient.delete(
        `/api/v1/resumes/${resumeId}`
      );

      setResumes((current) =>
        current.filter(
          (resume) =>
            resume.id !== resumeId
        )
      );

      setResumeMessage(
        "Resume deleted successfully."
      );
    } catch (err) {
      console.error(
        "Resume delete failed:",
        err
      );

      setResumeError(
        err?.message ||
          "Unable to delete resume."
      );
    }
  }

  /*
  |--------------------------------------------------------------------------
  | View resume
  |--------------------------------------------------------------------------
  */

  async function handleView(
    resume
  ) {
    try {
      setResumeError("");

      /*
       * Prefer the backend object_url if available.
       *
       * Your current ResumeResponse contains object_url.
       */
      if (resume?.object_url) {
        window.open(
          resume.object_url,
          "_blank",
          "noopener,noreferrer"
        );

        return;
      }

      /*
       * Fallback:
       * Fetch the specific resume row.
       *
       * This is useful if object_url was not returned.
       */
      const data =
        await apiClient.get(
          `/api/v1/resumes/${resume.id}`
        );

      if (data?.object_url) {
        window.open(
          data.object_url,
          "_blank",
          "noopener,noreferrer"
        );

        return;
      }

      setResumeError(
        "Resume URL is not available."
      );
    } catch (err) {
      console.error(
        "Unable to open resume:",
        err
      );

      setResumeError(
        err?.message ||
          "Unable to open resume."
      );
    }
  }

  /*
  |--------------------------------------------------------------------------
  | UI
  |--------------------------------------------------------------------------
  */

  return (
    <div className="space-y-6">

      <SectionHeader
        title="Resume"
        description="Upload, view or delete your current resume."
      />

      {resumeError && (
        <div className="rounded-xl border border-red-800 bg-red-950/40 px-4 py-3 text-sm text-red-300">
          {resumeError}
        </div>
      )}

      {resumeMessage && (
        <div className="rounded-xl border border-green-800 bg-green-950/40 px-4 py-3 text-sm text-green-300">
          {resumeMessage}
        </div>
      )}

      {/* Upload card */}

      <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-950 p-8">

        <div className="text-center">

          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-xl bg-blue-600/10 text-2xl">
            📄
          </div>

          <h3 className="mt-4 text-lg font-semibold">
            {resumes.length > 0
              ? "Replace Resume"
              : "Upload Resume"}
          </h3>

          <p className="mt-2 text-sm text-slate-500">
            PDF, DOC or DOCX · Maximum 10 MB
          </p>

          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.doc,.docx,application/pdf"
            onChange={handleUpload}
            className="hidden"
          />

          <button
            type="button"
            disabled={uploading}
            onClick={() =>
              inputRef.current?.click()
            }
            className="mt-6 rounded-lg bg-blue-600 px-5 py-3 text-sm font-semibold transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {uploading
              ? `Uploading ${progress}%`
              : resumes.length > 0
                ? "Upload New Resume"
                : "Choose Resume"}
          </button>

          {uploading && (
            <div className="mx-auto mt-5 max-w-md">

              <div className="h-2 overflow-hidden rounded-full bg-slate-800">
                <div
                  className="h-full bg-blue-600 transition-all"
                  style={{
                    width: `${progress}%`,
                  }}
                />
              </div>

              <p className="mt-2 text-xs text-slate-500">
                Uploading resume...
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Existing resume rows */}

      <div>
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold">
              Uploaded Resume
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Resume records connected to your account.
            </p>
          </div>

          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-400">
            {resumes.length}
          </span>
        </div>

        {resumes.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-700 p-10 text-center">

            <div className="text-3xl">
              📭
            </div>

            <p className="mt-3 text-sm text-slate-400">
              No resume uploaded yet.
            </p>

            <p className="mt-1 text-xs text-slate-600">
              Upload your resume to make it available
              across CareerForge.
            </p>
          </div>
        ) : (
          <div className="space-y-3">

            {resumes.map((resume) => (
              <ResumeRow
                key={resume.id}
                resume={resume}
                onView={() =>
                  handleView(resume)
                }
                onDelete={() =>
                  handleDelete(resume.id)
                }
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

/*
|--------------------------------------------------------------------------
| Resume row
|--------------------------------------------------------------------------
*/

function ResumeRow({
  resume,
  onView,
  onDelete,
}) {
  const fileSize =
    resume?.file_size
      ? formatFileSize(
          resume.file_size
        )
      : null;

  const createdAt =
    resume?.created_at
      ? new Date(
          resume.created_at
        ).toLocaleDateString()
      : null;

  return (
    <div className="flex flex-col justify-between gap-5 rounded-xl border border-slate-800 bg-slate-950 p-5 md:flex-row md:items-center">

      <div className="flex min-w-0 items-center gap-4">

        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-red-500/10 text-xl">
          📄
        </div>

        <div className="min-w-0">

          <h4 className="truncate font-semibold text-white">
            {resume?.file_name ||
              resume?.title ||
              "Resume"}
          </h4>

          <div className="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-xs text-slate-500">

            {fileSize && (
              <span>
                {fileSize}
              </span>
            )}

            {createdAt && (
              <span>
                Uploaded {createdAt}
              </span>
            )}

            {resume?.status && (
              <span className="text-green-400">
                {resume.status}
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="flex shrink-0 gap-2">

        <button
          type="button"
          onClick={onView}
          className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-semibold transition hover:bg-slate-800"
        >
          View
        </button>

        <button
          type="button"
          onClick={onDelete}
          className="rounded-lg border border-red-900 px-4 py-2 text-sm font-semibold text-red-400 transition hover:bg-red-950"
        >
          Delete
        </button>
      </div>
    </div>
  );
}

/*
|--------------------------------------------------------------------------
| Skills
|--------------------------------------------------------------------------
*/

function SkillsSection({
  skills,
  setSkills,
}) {
  const [adding, setAdding] =
    useState(false);

  const [form, setForm] =
    useState({
      name: "",
      category: "",
      proficiency: "",
      years_of_experience: "",
    });

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState("");

  async function addSkill(event) {
    event.preventDefault();

    try {
      setSaving(true);
      setError("");

      const created =
        await createSkill({
          name: form.name.trim(),

          category:
            form.category.trim() ||
            null,

          proficiency:
            form.proficiency.trim() ||
            null,

          years_of_experience:
            form.years_of_experience
              ? Number(
                  form.years_of_experience
                )
              : null,
        });

      setSkills((current) => [
        created,
        ...current,
      ]);

      setForm({
        name: "",
        category: "",
        proficiency: "",
        years_of_experience: "",
      });

      setAdding(false);
    } catch (err) {
      console.error(err);

      setError(
        err?.message ||
          "Unable to add skill."
      );
    } finally {
      setSaving(false);
    }
  }

  async function removeSkill(id) {
    if (
      !window.confirm(
        "Delete this skill?"
      )
    ) {
      return;
    }

    try {
      await deleteSkill(id);

      setSkills((current) =>
        current.filter(
          (skill) =>
            skill.id !== id
        )
      );
    } catch (err) {
      setError(
        err?.message ||
          "Unable to delete skill."
      );
    }
  }

  return (
    <div className="space-y-6">

      <SectionHeader
        title="Skills"
        description="Add and manage your professional skills."
      />

      {error && (
        <ErrorBox text={error} />
      )}

      <button
        type="button"
        onClick={() =>
          setAdding((value) => !value)
        }
        className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold hover:bg-blue-500"
      >
        {adding
          ? "Cancel"
          : "+ Add Skill"}
      </button>

      {adding && (
        <form
          onSubmit={addSkill}
          className="rounded-xl border border-slate-800 bg-slate-950 p-5"
        >
          <div className="grid gap-4 md:grid-cols-2">

            <Input
              label="Skill"
              value={form.name}
              onChange={(value) =>
                setForm({
                  ...form,
                  name: value,
                })
              }
              required
            />

            <Input
              label="Category"
              value={form.category}
              onChange={(value) =>
                setForm({
                  ...form,
                  category: value,
                })
              }
              placeholder="Cloud, Backend, DevOps..."
            />

            <Input
              label="Proficiency"
              value={form.proficiency}
              onChange={(value) =>
                setForm({
                  ...form,
                  proficiency: value,
                })
              }
              placeholder="Beginner / Intermediate / Advanced"
            />

            <Input
              label="Years of Experience"
              type="number"
              value={
                form.years_of_experience
              }
              onChange={(value) =>
                setForm({
                  ...form,
                  years_of_experience: value,
                })
              }
            />
          </div>

          <button
            type="submit"
            disabled={saving}
            className="mt-5 rounded-lg bg-white px-4 py-2 text-sm font-semibold text-slate-950 disabled:opacity-50"
          >
            {saving
              ? "Adding..."
              : "Add Skill"}
          </button>
        </form>
      )}

      {skills.length === 0 ? (
        <EmptyEditor text="No skills added yet." />
      ) : (
        <div className="space-y-3">
          {skills.map((skill) => (
            <SkillRow
              key={skill.id}
              skill={skill}
              skills={skills}
              setSkills={setSkills}
              onDelete={() =>
                removeSkill(skill.id)
              }
            />
          ))}
        </div>
      )}
    </div>
  );
}

function SkillRow({
  skill,
  skills,
  setSkills,
  onDelete,
}) {
  const [editing, setEditing] =
    useState(false);

  const [form, setForm] =
    useState({
      name: skill.name || "",
      category: skill.category || "",
      proficiency: skill.proficiency || "",
      years_of_experience:
        skill.years_of_experience ?? "",
    });

  const [saving, setSaving] =
    useState(false);

  async function save() {
    if (!form.name.trim()) {
      return;
    }

    try {
      setSaving(true);

      const updated =
        await updateSkill(
          skill.id,
          {
            name:
              form.name.trim(),

            category:
              form.category.trim() ||
              null,

            proficiency:
              form.proficiency.trim() ||
              null,

            years_of_experience:
              form.years_of_experience === ""
                ? null
                : Number(
                    form.years_of_experience
                  ),
          }
        );

      setSkills(
        skills.map((item) =>
          item.id === skill.id
            ? updated
            : item
        )
      );

      setEditing(false);
    } catch (err) {
      console.error(err);

      alert(
        err?.message ||
          "Unable to update skill."
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">

      {editing ? (
        <div className="space-y-5">

          <div className="grid gap-4 md:grid-cols-2">

            <Input
              label="Skill"
              value={form.name}
              onChange={(value) =>
                setForm({
                  ...form,
                  name: value,
                })
              }
              required
            />

            <Input
              label="Category"
              value={form.category}
              onChange={(value) =>
                setForm({
                  ...form,
                  category: value,
                })
              }
            />

            <Input
              label="Proficiency"
              value={form.proficiency}
              onChange={(value) =>
                setForm({
                  ...form,
                  proficiency: value,
                })
              }
            />

            <Input
              label="Years of Experience"
              type="number"
              value={
                form.years_of_experience
              }
              onChange={(value) =>
                setForm({
                  ...form,
                  years_of_experience:
                    value,
                })
              }
            />

          </div>

          <div className="flex gap-2">

            <button
              type="button"
              onClick={save}
              disabled={saving}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm disabled:opacity-50"
            >
              {saving
                ? "Saving..."
                : "Save"}
            </button>

            <button
              type="button"
              onClick={() =>
                setEditing(false)
              }
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm"
            >
              Cancel
            </button>

          </div>
        </div>
      ) : (
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">

          <div>

            <p className="font-semibold">
              {skill.name}
            </p>

            {skill.category && (
              <p className="mt-1 text-sm text-slate-500">
                {skill.category}
              </p>
            )}

            {skill.proficiency && (
              <p className="mt-1 text-xs text-blue-400">
                {skill.proficiency}
              </p>
            )}

            {skill.years_of_experience != null && (
              <p className="mt-1 text-xs text-slate-600">
                {skill.years_of_experience} years
              </p>
            )}

          </div>

          <div className="flex gap-2">

            <button
              type="button"
              onClick={() =>
                setEditing(true)
              }
              className="rounded-lg border border-slate-700 px-3 py-2 text-sm"
            >
              Edit
            </button>

            <button
              type="button"
              onClick={onDelete}
              className="rounded-lg border border-red-900 px-3 py-2 text-sm text-red-400"
            >
              Delete
            </button>

          </div>
        </div>
      )}
    </div>
  );
}


/*
|--------------------------------------------------------------------------
| Certifications
|--------------------------------------------------------------------------
*/

function CertificationSection({
  certifications,
  setCertifications,
}) {
  const [adding, setAdding] =
    useState(false);

  const [form, setForm] =
    useState({
      name: "",
      issuer: "",
      credential_id: "",
      credential_url: "",
      issue_date: "",
      expiry_date: "",
    });

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState("");

  async function addCertification(event) {
    event.preventDefault();

    try {
      setSaving(true);
      setError("");

      const created =
        await createCertification({
          name: form.name.trim(),

          issuer:
            form.issuer.trim(),

          credential_id:
            form.credential_id.trim() ||
            null,

          credential_url:
            form.credential_url.trim() ||
            null,

          issue_date:
            form.issue_date || null,

          expiry_date:
            form.expiry_date || null,
        });

      setCertifications((current) => [
        created,
        ...current,
      ]);

      setForm({
        name: "",
        issuer: "",
        credential_id: "",
        credential_url: "",
        issue_date: "",
        expiry_date: "",
      });

      setAdding(false);
    } catch (err) {
      console.error(err);

      setError(
        err?.message ||
          "Unable to add certification."
      );
    } finally {
      setSaving(false);
    }
  }

  async function removeCertification(id) {
    if (
      !window.confirm(
        "Delete this certification?"
      )
    ) {
      return;
    }

    try {
      await deleteCertification(id);

      setCertifications((current) =>
        current.filter(
          (item) => item.id !== id
        )
      );
    } catch (err) {
      setError(
        err?.message ||
          "Unable to delete certification."
      );
    }
  }

  return (
    <div className="space-y-6">

      <SectionHeader
        title="Certifications"
        description="Manage your professional certifications and credentials."
      />

      {error && (
        <ErrorBox text={error} />
      )}

      <button
        type="button"
        onClick={() =>
          setAdding((value) => !value)
        }
        className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold hover:bg-blue-500"
      >
        {adding
          ? "Cancel"
          : "+ Add Certification"}
      </button>

      {adding && (
        <form
          onSubmit={addCertification}
          className="space-y-5 rounded-xl border border-slate-800 bg-slate-950 p-5"
        >
          <div className="grid gap-4 md:grid-cols-2">

            <Input
              label="Certification Name"
              value={form.name}
              onChange={(value) =>
                setForm({
                  ...form,
                  name: value,
                })
              }
              required
            />

            <Input
              label="Issuing Organization"
              value={form.issuer}
              onChange={(value) =>
                setForm({
                  ...form,
                  issuer: value,
                })
              }
              required
            />

            <Input
              label="Credential ID"
              value={form.credential_id}
              onChange={(value) =>
                setForm({
                  ...form,
                  credential_id: value,
                })
              }
            />

            <Input
              label="Credential URL"
              type="url"
              value={form.credential_url}
              onChange={(value) =>
                setForm({
                  ...form,
                  credential_url: value,
                })
              }
            />

            <Input
              label="Issue Date"
              type="date"
              value={form.issue_date}
              onChange={(value) =>
                setForm({
                  ...form,
                  issue_date: value,
                })
              }
            />

            <Input
              label="Expiry Date"
              type="date"
              value={form.expiry_date}
              onChange={(value) =>
                setForm({
                  ...form,
                  expiry_date: value,
                })
              }
            />

          </div>

          <button
            type="submit"
            disabled={saving}
            className="rounded-lg bg-white px-4 py-2 font-semibold text-slate-950 disabled:opacity-50"
          >
            {saving
              ? "Adding..."
              : "Add Certification"}
          </button>
        </form>
      )}

      {certifications.length === 0 ? (
        <EmptyEditor
          text="No certifications added yet."
        />
      ) : (
        <div className="space-y-3">

          {certifications.map(
            (certification) => (
              <CertificationRow
                key={certification.id}
                certification={certification}
                certifications={certifications}
                setCertifications={
                  setCertifications
                }
                onDelete={() =>
                  removeCertification(
                    certification.id
                  )
                }
              />
            )
          )}

        </div>
      )}
    </div>
  );
}

function CertificationRow({
  certification,
  onDelete,
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">

        <div className="min-w-0">
          <h3 className="font-semibold text-white">
            {certification.name}
          </h3>

          <p className="mt-1 text-sm text-slate-400">
            {certification.issuer}
          </p>

          <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500">

            {certification.issue_date && (
              <span>
                Issued{" "}
                {formatEditorDate(
                  certification.issue_date
                )}
              </span>
            )}

            {certification.expiry_date && (
              <span>
                Expires{" "}
                {formatEditorDate(
                  certification.expiry_date
                )}
              </span>
            )}

            {certification.credential_id && (
              <span>
                ID {certification.credential_id}
              </span>
            )}

          </div>

          {certification.credential_url && (
            <a
              href={certification.credential_url}
              target="_blank"
              rel="noreferrer"
              className="mt-2 inline-block text-xs text-blue-400 hover:text-blue-300"
            >
              View credential ↗
            </a>
          )}
        </div>

        <button
          type="button"
          onClick={onDelete}
          className="rounded-lg border border-red-900 px-3 py-2 text-sm text-red-400 hover:bg-red-950/40"
        >
          Delete
        </button>

      </div>
    </div>
  );
}

function formatEditorDate(value) {
  if (!value) return "";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleDateString(
    undefined,
    {
      day: "numeric",
      month: "short",
      year: "numeric",
    }
  );
}

/*
|--------------------------------------------------------------------------
| Projects
|--------------------------------------------------------------------------
*/

function ProjectsSection({
  projects,
  setProjects,
}) {
  const [adding, setAdding] =
    useState(false);

  const [form, setForm] =
    useState({
      name: "",
      description: "",
      technologies: "",
      github_url: "",
      live_url: "",
      start_date: "",
      end_date: "",
    });

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState("");

  async function addProject(event) {
    event.preventDefault();

    try {
      setSaving(true);
      setError("");

      const created =
        await createProject({
          name: form.name.trim(),

          description:
            form.description.trim() ||
            null,

          technologies:
            form.technologies
              .split(",")
              .map((item) =>
                item.trim()
              )
              .filter(Boolean),

          github_url:
            form.github_url.trim() ||
            null,

          live_url:
            form.live_url.trim() ||
            null,

          start_date:
            form.start_date || null,

          end_date:
            form.end_date || null,
        });

      setProjects((current) => [
        created,
        ...current,
      ]);

      setForm({
        name: "",
        description: "",
        technologies: "",
        github_url: "",
        live_url: "",
        start_date: "",
        end_date: "",
      });

      setAdding(false);
    } catch (err) {
      console.error(err);

      setError(
        err?.message ||
          "Unable to add project."
      );
    } finally {
      setSaving(false);
    }
  }

  async function removeProject(id) {
    if (
      !window.confirm(
        "Delete this project?"
      )
    ) {
      return;
    }

    try {
      await deleteProject(id);

      setProjects((current) =>
        current.filter(
          (project) =>
            project.id !== id
        )
      );
    } catch (err) {
      setError(
        err?.message ||
          "Unable to delete project."
      );
    }
  }

  return (
    <div className="space-y-6">

      <SectionHeader
        title="Projects"
        description="Manage your projects and portfolio work."
      />

      {error && (
        <ErrorBox text={error} />
      )}

      <button
        type="button"
        onClick={() =>
          setAdding((value) => !value)
        }
        className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold hover:bg-blue-500"
      >
        {adding
          ? "Cancel"
          : "+ Add Project"}
      </button>

      {adding && (
        <form
          onSubmit={addProject}
          className="space-y-5 rounded-xl border border-slate-800 bg-slate-950 p-5"
        >
          <Input
            label="Project Name"
            value={form.name}
            onChange={(value) =>
              setForm({
                ...form,
                name: value,
              })
            }
            required
          />

          <TextArea
            label="Description"
            value={form.description}
            onChange={(value) =>
              setForm({
                ...form,
                description: value,
              })
            }
          />

          <Input
            label="Technologies"
            value={form.technologies}
            onChange={(value) =>
              setForm({
                ...form,
                technologies: value,
              })
            }
            placeholder="AWS, Docker, Kubernetes, FastAPI"
          />

          <div className="grid gap-4 md:grid-cols-2">

            <Input
              label="GitHub URL"
              type="url"
              value={form.github_url}
              onChange={(value) =>
                setForm({
                  ...form,
                  github_url: value,
                })
              }
            />

            <Input
              label="Live URL"
              type="url"
              value={form.live_url}
              onChange={(value) =>
                setForm({
                  ...form,
                  live_url: value,
                })
              }
            />

            <Input
              label="Start Date"
              type="date"
              value={form.start_date}
              onChange={(value) =>
                setForm({
                  ...form,
                  start_date: value,
                })
              }
            />

            <Input
              label="End Date"
              type="date"
              value={form.end_date}
              onChange={(value) =>
                setForm({
                  ...form,
                  end_date: value,
                })
              }
            />
          </div>

          <button
            type="submit"
            disabled={saving}
            className="rounded-lg bg-white px-4 py-2 font-semibold text-slate-950 disabled:opacity-50"
          >
            {saving
              ? "Adding..."
              : "Add Project"}
          </button>
        </form>
      )}

      {projects.length === 0 ? (
        <EmptyEditor text="No projects added yet." />
      ) : (
        <div className="space-y-3">

          {projects.map((project) => (
            <ProjectRow
              key={project.id}
              project={project}
              projects={projects}
              setProjects={setProjects}
              onDelete={() =>
                removeProject(project.id)
              }
            />
          ))}
        </div>
      )}
    </div>
  );
}

function ProjectRow({
  project,
  projects,
  setProjects,
  onDelete,
}) {
  const [editing, setEditing] =
    useState(false);

  const [form, setForm] =
    useState({
      name: project.name || "",
      description:
        project.description || "",
      technologies:
        Array.isArray(project.technologies)
          ? project.technologies.join(", ")
          : "",
      github_url:
        project.github_url || "",
      live_url:
        project.live_url || "",
      start_date:
        project.start_date || "",
      end_date:
        project.end_date || "",
    });

  const [saving, setSaving] =
    useState(false);

  async function save() {
    if (!form.name.trim()) {
      return;
    }

    try {
      setSaving(true);

      const updated =
        await updateProject(
          project.id,
          {
            name:
              form.name.trim(),

            description:
              form.description.trim() ||
              null,

            technologies:
              form.technologies
                .split(",")
                .map((item) =>
                  item.trim()
                )
                .filter(Boolean),

            github_url:
              form.github_url.trim() ||
              null,

            live_url:
              form.live_url.trim() ||
              null,

            start_date:
              form.start_date || null,

            end_date:
              form.end_date || null,
          }
        );

      setProjects(
        projects.map((item) =>
          item.id === project.id
            ? updated
            : item
        )
      );

      setEditing(false);
    } catch (err) {
      console.error(err);

      alert(
        err?.message ||
          "Unable to update project."
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">

      {editing ? (
        <div className="space-y-5">

          <Input
            label="Project Name"
            value={form.name}
            onChange={(value) =>
              setForm({
                ...form,
                name: value,
              })
            }
            required
          />

          <TextArea
            label="Description"
            value={form.description}
            onChange={(value) =>
              setForm({
                ...form,
                description: value,
              })
            }
          />

          <Input
            label="Technologies"
            value={form.technologies}
            onChange={(value) =>
              setForm({
                ...form,
                technologies: value,
              })
            }
            placeholder="AWS, Docker, Kubernetes, FastAPI"
          />

          <div className="grid gap-4 md:grid-cols-2">

            <Input
              label="GitHub URL"
              type="url"
              value={form.github_url}
              onChange={(value) =>
                setForm({
                  ...form,
                  github_url: value,
                })
              }
            />

            <Input
              label="Live URL"
              type="url"
              value={form.live_url}
              onChange={(value) =>
                setForm({
                  ...form,
                  live_url: value,
                })
              }
            />

            <Input
              label="Start Date"
              type="date"
              value={form.start_date}
              onChange={(value) =>
                setForm({
                  ...form,
                  start_date: value,
                })
              }
            />

            <Input
              label="End Date"
              type="date"
              value={form.end_date}
              onChange={(value) =>
                setForm({
                  ...form,
                  end_date: value,
                })
              }
            />

          </div>

          <div className="flex gap-2">

            <button
              type="button"
              onClick={save}
              disabled={saving}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm disabled:opacity-50"
            >
              {saving
                ? "Saving..."
                : "Save"}
            </button>

            <button
              type="button"
              onClick={() =>
                setEditing(false)
              }
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm"
            >
              Cancel
            </button>

          </div>
        </div>
      ) : (
        <div className="flex flex-col justify-between gap-4 sm:flex-row">

          <div>

            <h3 className="font-semibold">
              {project.name}
            </h3>

            {project.description && (
              <p className="mt-2 text-sm text-slate-500">
                {project.description}
              </p>
            )}

            {project.technologies?.length >
              0 && (
              <div className="mt-3 flex flex-wrap gap-2">

                {project.technologies.map(
                  (technology) => (
                    <span
                      key={technology}
                      className="rounded bg-slate-800 px-2 py-1 text-xs text-slate-400"
                    >
                      {technology}
                    </span>
                  )
                )}

              </div>
            )}

          </div>

          <div className="flex gap-2">

            <button
              type="button"
              onClick={() =>
                setEditing(true)
              }
              className="rounded-lg border border-slate-700 px-3 py-2 text-sm"
            >
              Edit
            </button>

            <button
              type="button"
              onClick={onDelete}
              className="rounded-lg border border-red-900 px-3 py-2 text-sm text-red-400"
            >
              Delete
            </button>

          </div>
        </div>
      )}
    </div>
  );
}

/*
|--------------------------------------------------------------------------
| Experience
|--------------------------------------------------------------------------
*/

function ExperienceSection({
  experience,
  setExperience,
}) {
  const [adding, setAdding] =
    useState(false);

  const [form, setForm] =
    useState({
      company: "",
      job_title: "",
      employment_type: "",
      location: "",
      start_date: "",
      end_date: "",
      is_current: false,
      description: "",
    });

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState("");

  async function addExperience(event) {
    event.preventDefault();

    try {
      setSaving(true);
      setError("");

      const created =
        await createExperience({
          company:
            form.company.trim(),

          job_title:
            form.job_title.trim(),

          employment_type:
            form.employment_type.trim() ||
            null,

          location:
            form.location.trim() ||
            null,

          start_date:
            form.start_date || null,

          end_date:
            form.is_current
              ? null
              : form.end_date || null,

          is_current:
            form.is_current,

          description:
            form.description.trim() ||
            null,
        });

      setExperience((current) => [
        created,
        ...current,
      ]);

      setForm({
        company: "",
        job_title: "",
        employment_type: "",
        location: "",
        start_date: "",
        end_date: "",
        is_current: false,
        description: "",
      });

      setAdding(false);
    } catch (err) {
      console.error(err);

      setError(
        err?.message ||
          "Unable to add experience."
      );
    } finally {
      setSaving(false);
    }
  }

  async function removeExperience(
    id
  ) {
    if (
      !window.confirm(
        "Delete this experience?"
      )
    ) {
      return;
    }

    try {
      await deleteExperience(id);

      setExperience((current) =>
        current.filter(
          (item) =>
            item.id !== id
        )
      );
    } catch (err) {
      setError(
        err?.message ||
          "Unable to delete experience."
      );
    }
  }

  return (
    <div className="space-y-6">

      <SectionHeader
        title="Experience"
        description="Manage jobs, internships and work experience."
      />

      {error && (
        <ErrorBox text={error} />
      )}

      <button
        type="button"
        onClick={() =>
          setAdding((value) => !value)
        }
        className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold hover:bg-blue-500"
      >
        {adding
          ? "Cancel"
          : "+ Add Experience"}
      </button>

      {adding && (
        <form
          onSubmit={addExperience}
          className="space-y-5 rounded-xl border border-slate-800 bg-slate-950 p-5"
        >
          <div className="grid gap-4 md:grid-cols-2">

            <Input
              label="Company"
              value={form.company}
              onChange={(value) =>
                setForm({
                  ...form,
                  company: value,
                })
              }
              required
            />

            <Input
              label="Job Title"
              value={form.job_title}
              onChange={(value) =>
                setForm({
                  ...form,
                  job_title: value,
                })
              }
              required
            />

            <Input
              label="Employment Type"
              value={
                form.employment_type
              }
              onChange={(value) =>
                setForm({
                  ...form,
                  employment_type: value,
                })
              }
              placeholder="Full-time / Internship"
            />

            <Input
              label="Location"
              value={form.location}
              onChange={(value) =>
                setForm({
                  ...form,
                  location: value,
                })
              }
            />
          </div>

          <div className="grid gap-4 md:grid-cols-2">

            <Input
              label="Start Date"
              type="date"
              value={form.start_date}
              onChange={(value) =>
                setForm({
                  ...form,
                  start_date: value,
                })
              }
            />

            {!form.is_current && (
              <Input
                label="End Date"
                type="date"
                value={form.end_date}
                onChange={(value) =>
                  setForm({
                    ...form,
                    end_date: value,
                  })
                }
              />
            )}
          </div>

          <label className="flex items-center gap-3 text-sm text-slate-400">

            <input
              type="checkbox"
              checked={form.is_current}
              onChange={(event) =>
                setForm({
                  ...form,
                  is_current:
                    event.target.checked,
                })
              }
            />

            Currently working here
          </label>

          <TextArea
            label="Description"
            value={form.description}
            onChange={(value) =>
              setForm({
                ...form,
                description: value,
              })
            }
          />

          <button
            type="submit"
            disabled={saving}
            className="rounded-lg bg-white px-4 py-2 font-semibold text-slate-950 disabled:opacity-50"
          >
            {saving
              ? "Adding..."
              : "Add Experience"}
          </button>
        </form>
      )}

      {experience.length === 0 ? (
        <EmptyEditor text="No experience added yet." />
      ) : (
        <div className="space-y-3">

          {experience.map((item) => (
            <ExperienceRow
              key={item.id}
              item={item}
              experience={experience}
              setExperience={
                setExperience
              }
              onDelete={() =>
                removeExperience(
                  item.id
                )
              }
            />
          ))}
        </div>
      )}
    </div>
  );
}

function ExperienceRow({
  item,
  experience,
  setExperience,
  onDelete,
}) {
  const [editing, setEditing] =
    useState(false);

  const [form, setForm] =
    useState({
      company:
        item.company || "",

      job_title:
        item.job_title || "",

      employment_type:
        item.employment_type || "",

      location:
        item.location || "",

      start_date:
        item.start_date || "",

      end_date:
        item.end_date || "",

      is_current:
        item.is_current || false,

      description:
        item.description || "",
    });

  const [saving, setSaving] =
    useState(false);

  async function save() {
    if (
      !form.company.trim() ||
      !form.job_title.trim()
    ) {
      return;
    }

    try {
      setSaving(true);

      const updated =
        await updateExperience(
          item.id,
          {
            company:
              form.company.trim(),

            job_title:
              form.job_title.trim(),

            employment_type:
              form.employment_type.trim() ||
              null,

            location:
              form.location.trim() ||
              null,

            start_date:
              form.start_date || null,

            end_date:
              form.is_current
                ? null
                : form.end_date || null,

            is_current:
              form.is_current,

            description:
              form.description.trim() ||
              null,
          }
        );

      setExperience(
        experience.map((entry) =>
          entry.id === item.id
            ? updated
            : entry
        )
      );

      setEditing(false);
    } catch (err) {
      console.error(err);

      alert(
        err?.message ||
          "Unable to update experience."
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">

      {editing ? (
        <div className="space-y-5">

          <div className="grid gap-4 md:grid-cols-2">

            <Input
              label="Company"
              value={form.company}
              onChange={(value) =>
                setForm({
                  ...form,
                  company: value,
                })
              }
              required
            />

            <Input
              label="Job Title"
              value={form.job_title}
              onChange={(value) =>
                setForm({
                  ...form,
                  job_title: value,
                })
              }
              required
            />

            <Input
              label="Employment Type"
              value={
                form.employment_type
              }
              onChange={(value) =>
                setForm({
                  ...form,
                  employment_type:
                    value,
                })
              }
              placeholder="Full-time / Internship"
            />

            <Input
              label="Location"
              value={form.location}
              onChange={(value) =>
                setForm({
                  ...form,
                  location: value,
                })
              }
            />

          </div>

          <div className="grid gap-4 md:grid-cols-2">

            <Input
              label="Start Date"
              type="date"
              value={form.start_date}
              onChange={(value) =>
                setForm({
                  ...form,
                  start_date: value,
                })
              }
            />

            {!form.is_current && (
              <Input
                label="End Date"
                type="date"
                value={form.end_date}
                onChange={(value) =>
                  setForm({
                    ...form,
                    end_date: value,
                  })
                }
              />
            )}

          </div>

          <label className="flex items-center gap-3 text-sm text-slate-400">

            <input
              type="checkbox"
              checked={form.is_current}
              onChange={(event) =>
                setForm({
                  ...form,
                  is_current:
                    event.target.checked,
                  end_date:
                    event.target.checked
                      ? ""
                      : form.end_date,
                })
              }
            />

            Currently working here

          </label>

          <TextArea
            label="Description"
            value={form.description}
            onChange={(value) =>
              setForm({
                ...form,
                description: value,
              })
            }
          />

          <div className="flex gap-2">

            <button
              type="button"
              onClick={save}
              disabled={saving}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm disabled:opacity-50"
            >
              {saving
                ? "Saving..."
                : "Save"}
            </button>

            <button
              type="button"
              onClick={() =>
                setEditing(false)
              }
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm"
            >
              Cancel
            </button>

          </div>
        </div>
      ) : (
        <div className="flex flex-col justify-between gap-4 sm:flex-row">

          <div>

            <h3 className="font-semibold">
              {item.job_title}
            </h3>

            <p className="mt-1 text-blue-400">
              {item.company}
            </p>

            {item.employment_type && (
              <p className="mt-1 text-sm text-slate-500">
                {item.employment_type}
              </p>
            )}

            {item.location && (
              <p className="mt-1 text-sm text-slate-600">
                {item.location}
              </p>
            )}

            {(item.start_date ||
              item.end_date ||
              item.is_current) && (
              <p className="mt-2 text-xs text-slate-600">
                {item.start_date ||
                  "N/A"}
                {" → "}
                {item.is_current
                  ? "Present"
                  : item.end_date ||
                    "N/A"}
              </p>
            )}

            {item.description && (
              <p className="mt-3 text-sm leading-6 text-slate-500">
                {item.description}
              </p>
            )}

          </div>

          <div className="flex gap-2">

            <button
              type="button"
              onClick={() =>
                setEditing(true)
              }
              className="rounded-lg border border-slate-700 px-3 py-2 text-sm"
            >
              Edit
            </button>

            <button
              type="button"
              onClick={onDelete}
              className="rounded-lg border border-red-900 px-3 py-2 text-sm text-red-400"
            >
              Delete
            </button>

          </div>
        </div>
      )}
    </div>
  );
}

/*
|--------------------------------------------------------------------------
| Reusable components
|--------------------------------------------------------------------------
*/

function SectionHeader({
  title,
  description,
}) {
  return (
    <div>
      <h2 className="text-2xl font-semibold">
        {title}
      </h2>

      <p className="mt-2 text-sm text-slate-500">
        {description}
      </p>
    </div>
  );
}

function Input({
  label,
  value,
  onChange,
  type = "text",
  placeholder = "",
  required = false,
}) {
  const inputId =
    `input-${label
      .toLowerCase()
      .replace(/\s+/g, "-")}`;

  return (
    <div>
      <label
        htmlFor={inputId}
        className="mb-2 block text-sm text-slate-300"
      >
        {label}
      </label>

      <input
        id={inputId}
        type={type}
        value={value ?? ""}
        onChange={(event) =>
          onChange(
            event.target.value
          )
        }
        placeholder={placeholder}
        required={required}
        className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-blue-500"
      />
    </div>
  );
}

function TextArea({
  label,
  value,
  onChange,
}) {
  const textareaId =
    `textarea-${label
      .toLowerCase()
      .replace(/\s+/g, "-")}`;

  return (
    <div>
      <label
        htmlFor={textareaId}
        className="mb-2 block text-sm text-slate-300"
      >
        {label}
      </label>

      <textarea
        id={textareaId}
        value={value ?? ""}
        onChange={(event) =>
          onChange(
            event.target.value
          )
        }
        rows={6}
        className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-blue-500"
      />
    </div>
  );
}

function SaveButton({
  saving,
}) {
  return (
    <button
      type="submit"
      disabled={saving}
      className="rounded-lg bg-blue-600 px-5 py-3 font-semibold transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
    >
      {saving
        ? "Saving..."
        : "Save Changes"}
    </button>
  );
}

function EmptyEditor({
  text,
}) {
  return (
    <div className="rounded-xl border border-dashed border-slate-700 p-10 text-center text-sm text-slate-500">
      {text}
    </div>
  );
}

function ErrorBox({
  text,
}) {
  return (
    <div className="rounded-lg border border-red-800 bg-red-950/30 px-4 py-3 text-sm text-red-300">
      {text}
    </div>
  );
}

/*
|--------------------------------------------------------------------------
| File size helper
|--------------------------------------------------------------------------
*/

function formatFileSize(
  bytes
) {
  if (!bytes) {
    return "0 Bytes";
  }

  const units = [
    "Bytes",
    "KB",
    "MB",
    "GB",
  ];

  const index = Math.floor(
    Math.log(bytes) /
      Math.log(1024)
  );

  const safeIndex = Math.min(
    index,
    units.length - 1
  );

  return `${(
    bytes /
    Math.pow(
      1024,
      safeIndex
    )
  ).toFixed(
    safeIndex === 0 ? 0 : 2
  )} ${units[safeIndex]}`;
}