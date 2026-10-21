# Design: Shared Documents

**Author:** Priya Raman (Platform team) · **Reviewers:** Dan K., Wei L. · **Status:** Draft, targeting Q3

## Background

Customers on Teamboard (our multi-tenant project management SaaS) keep asking
for a place to keep files next to their projects. Today they paste Google
Drive links into task comments, which breaks when people leave the company and
gives us no way to preview files inline. Shared Documents adds first-class
file storage to each workspace, with previews and the ability to share a
document with people outside the workspace (clients, contractors).

## Goals

- Upload files (any type, up to "large" — see Storage) to a project.
- Inline preview: thumbnails in the file list, and in-browser viewing for
  images, PDFs, and HTML exports from other tools.
- Import a file from a URL (e.g. a public Dropbox or S3 link) without the user
  downloading it first.
- Share a single document with anyone via a link, no Teamboard account needed.
- Ship an MVP in 6 weeks with two engineers.

## Non-goals

- Real-time co-editing.
- Folder hierarchies (flat list per project for v1).
- Fine-grained per-document permissions inside a workspace — anyone in the
  workspace can see all its documents, same as tasks today.

## Architecture overview

```
Browser ──> app.teamboard.io (Rails API + web UI, ECS)
               │
               ├── Postgres (shared cluster; documents table, tenant_id column)
               ├── S3 bucket teamboard-docs (key: <tenant_id>/<doc_id>/<filename>)
               └── SQS thumbnails queue ──> thumbnail-worker (ECS, ImageMagick)
                                                 └── writes <tenant_id>/<doc_id>/thumb.png to S3
```

All services run in the existing production VPC and use the standard
`teamboard-app` task role, which already has access to the docs bucket, SQS,
and Secrets Manager. The admin console (`app.teamboard.io/admin`) is unchanged.

## API

All endpoints except `/share/*` require the normal session cookie and are
scoped to the caller's current workspace.

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/projects/:id/documents/upload-url` | Returns a presigned S3 PUT URL and a new `doc_id`. Client uploads directly to S3, then calls `complete`. |
| `POST` | `/api/documents/:doc_id/complete` | Marks upload complete, records `content_type` from the client's upload, enqueues thumbnail job. |
| `POST` | `/api/projects/:id/documents/import` | Body `{ "url": "..." }`. Server downloads the file from the URL and stores it as a new document. Enqueues thumbnail job. |
| `GET` | `/api/projects/:id/documents` | Lists documents in the project. |
| `GET` | `/documents/:doc_id/view` | Streams the file from S3 through the app for inline viewing, with the stored `content_type`. |
| `POST` | `/api/documents/:doc_id/share` | Enables the public share link for a document. |
| `DELETE` | `/api/documents/:doc_id/share` | Disables it. |
| `GET` | `/share/:doc_id` | Public page; renders the document inline (same handler as `/view`) for anyone with the link. |

## Data model

```sql
CREATE TABLE documents (
  id            BIGSERIAL PRIMARY KEY,
  tenant_id     BIGINT NOT NULL REFERENCES tenants(id),
  project_id    BIGINT NOT NULL REFERENCES projects(id),
  uploaded_by   BIGINT NOT NULL REFERENCES users(id),
  filename      TEXT NOT NULL,
  content_type  TEXT NOT NULL,
  size_bytes    BIGINT,
  s3_key        TEXT NOT NULL,
  shared        BOOLEAN NOT NULL DEFAULT false,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON documents (tenant_id, project_id);
```

Share links are simply `https://app.teamboard.io/share/<id>` while `shared =
true`, which keeps them short and easy to paste into email.

## Storage and uploads

Uploads go straight from the browser to S3 via presigned PUT URLs so large
files don't pass through the Rails processes. The presigned URL is generated
with the object key and a 1-hour expiry. We aren't setting a hard size limit
for v1 — customers have asked for video uploads and we'd rather learn what
sizes they need before choosing a number. Storage is billed to us on S3's
standard tier; we'll revisit pricing tiers once we see usage.

`size_bytes` is filled in by the `complete` call from the S3 object's
metadata.

## Import from URL

The import endpoint uses the same HTTP client library as our integrations
(Faraday with redirects enabled, 60s timeout). It downloads the response body
to a temp file, takes the filename from the URL path and the content type
from the response header, uploads to S3, and inserts a `documents` row. This
lets users pull in files from Dropbox, Box, public S3 buckets, and internal
wiki exports without a round trip through their laptop.

## Thumbnails and previews

On every `complete` and `import`, we enqueue `{tenant_id, doc_id, s3_key}` to
the thumbnails queue. `thumbnail-worker` downloads the object and runs:

```
convert <input>[0] -thumbnail 320x320 thumb.png
```

ImageMagick handles images, PDFs (via Ghostscript), SVG, and most other
formats our customers use, so we get thumbnails for almost everything with one
command. The worker uses the distro ImageMagick package and default policy.
If `convert` fails we show a generic file icon.

Inline viewing (`/view` and `/share`) streams the S3 object through the app
with `Content-Type` set to the stored `content_type` so that browsers render
images, PDFs, and HTML exports in place rather than downloading them.

## Observability

- Datadog metrics: uploads/min, import failures, thumbnail queue depth and
  job duration.
- Rails request logs (7-day retention) as for every other endpoint.
- Sentry for worker exceptions.

## Rollout

1. Behind the `shared_documents` feature flag, enabled for internal workspace.
2. Beta with 20 design-partner workspaces (two weeks).
3. GA to all paid plans; free plan gets it one month later.

Rollback: disable the flag. Uploaded objects remain in S3.

## Open questions

- Should free-plan workspaces get a smaller per-file cap? (Leaning no for simplicity.)
- Do we need virus scanning before GA? (Probably post-GA.)
