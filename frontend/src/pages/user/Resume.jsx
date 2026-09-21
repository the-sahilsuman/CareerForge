import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  getResumes,
  uploadResume,
} from "../../services/api/resumeApi";

export default function Resume() {
  const [resume, setResume] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [uploading, setUploading] =
    useState(false);

  const inputRef =
    useRef(null);

  useEffect(() => {
    loadResume();
  }, []);

  async function loadResume() {
    try {
      setLoading(true);

      const data =
        await getResumes();

      setResume(
        data?.length
          ? data[0]
          : null
      );

    } catch (error) {
      console.error(
        "Unable to load resume:",
        error
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleUpload(event) {
    const file =
      event.target.files?.[0];

    if (!file) {
      return;
    }

    try {
      setUploading(true);

      const uploaded =
        await uploadResume(file);

      setResume(uploaded);

    } catch (error) {
      console.error(
        "Resume upload failed:",
        error
      );

      alert(
        error?.message ||
          "Unable to upload resume."
      );
    } finally {
      setUploading(false);

      event.target.value = "";
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 p-8 text-white">

      <div className="mx-auto max-w-5xl">

        <div className="mb-8">

          <p className="text-sm text-slate-500">
            CareerForge
          </p>

          <h1 className="mt-2 text-3xl font-bold">
            Resume
          </h1>

          <p className="mt-2 text-slate-400">
            Keep your latest resume available for your
            applications.
          </p>

        </div>

        {loading ? (
          <p className="text-slate-500">
            Loading resume...
          </p>
        ) : (
          <div className="grid gap-6 md:grid-cols-2">

            {/* Update */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

              <div className="mb-5 text-3xl">
                ↑
              </div>

              <h2 className="text-xl font-semibold">
                Update Resume
              </h2>

              <p className="mt-2 text-sm leading-6 text-slate-500">
                Upload a new PDF resume. Your latest
                uploaded resume will be available here.
              </p>

              <input
                ref={inputRef}
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleUpload}
                className="hidden"
              />

              <button
                type="button"
                disabled={uploading}
                onClick={() =>
                  inputRef.current?.click()
                }
                className="mt-6 rounded-lg bg-blue-600 px-5 py-3 text-sm font-semibold hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {uploading
                  ? "Uploading..."
                  : resume
                    ? "Upload New Resume"
                    : "Upload Resume"}
              </button>

            </div>

            {/* View */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

              <div className="mb-5 text-3xl">
                📄
              </div>

              <h2 className="text-xl font-semibold">
                View Resume
              </h2>

              {resume ? (
                <>
                  <p className="mt-2 truncate text-sm text-slate-500">
                    {resume.file_name}
                  </p>

                  <a
                    href={resume.object_url}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-6 inline-block rounded-lg bg-white px-5 py-3 text-sm font-semibold text-slate-950 hover:bg-slate-200"
                  >
                    Open Resume
                  </a>
                </>
              ) : (
                <>
                  <p className="mt-2 text-sm text-slate-500">
                    No resume uploaded yet.
                  </p>

                  <button
                    type="button"
                    onClick={() =>
                      inputRef.current?.click()
                    }
                    className="mt-6 rounded-lg border border-slate-700 px-5 py-3 text-sm font-semibold hover:bg-slate-800"
                  >
                    Upload Resume
                  </button>
                </>
              )}

            </div>

          </div>
        )}

      </div>

    </div>
  );
}