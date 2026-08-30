# Cream Beans — User-Facing Frontend

React + Vite + Tailwind CSS frontend for the Cream Beans Lost & Found system.
This package owns **only** the end-user web app — it does not touch the
backend, the AI matcher, or the database.

## Stack

- React 19 + Vite 7
- Tailwind CSS v4
- React Router v7

## Getting started

```bash
npm install
cp .env.example .env   # already present with mock mode on
npm run dev
```

The app boots straight into **mock mode** — every form submission is
handled by an in-memory fake matcher (`src/api/mockData.js`), so the whole
flow (Report Lost → AI Processing → Potential Matches → Match Score →
Item Details, and Report Found) works with zero backend running. Occasional
simulated failures (network error / image upload failure) are built in so
those UI states are demoable.

## Switching to the real backend

Edit `.env`:

```bash
VITE_USE_MOCK_API=false
VITE_API_BASE_URL=http://localhost:8000   # your FastAPI base URL
```

No component code needs to change — `src/api/client.js` is the single
place that knows about mock vs. real, and every page only ever calls
`reportLost()` / `reportFound()` from that file.

## Project structure

```
src/
  api/
    client.js       # mock <-> real backend switch, error handling
    mockData.js      # fake found-item pool + naive local scorer
  components/        # form fields, image upload, match card, the
                      # signature status-flow + match-score-stamp, states
  pages/
    Landing.jsx
    ReportLost.jsx
    ReportFound.jsx
    MatchResults.jsx
    ItemDetails.jsx
    NotFound.jsx
```

## Screens delivered (per spec)

1. **Landing** — explains "Find what you lost", Report Lost / Report Found CTAs.
2. **Report Lost** — category, description, image, location, date/time, name,
   email, phone → `POST /items/lost`.
3. **Report Found** — same fields → `POST /items/found`.
4. **Match Results** — shown right after a lost report is submitted; each
   card shows image, category, description, location, date/time, match
   score, and the finder's contact details. Sorted by `final_score`
   descending.
5. **Item Details** — full found-item info + finder contact.
6. **Empty / error / loading states** — no matches, backend unavailable,
   image upload failure, invalid form, loading — all implemented (see
   `src/components/StateViews.jsx`).

## API contract used

Per the spec, this frontend only calls the two endpoints below and invents
nothing else:

- `POST /items/lost` — multipart/form-data: `category, description, image,
  location, datetime, name, email, phone`
- `POST /items/found` — same fields, multipart/form-data

### ⚠️ Open questions for the tech lead

The spec doesn't define response shapes or how "Potential Matches" and
"Item Details" get their data, so this frontend makes the following
assumptions. Please confirm or correct — the two functions in
`src/api/client.js` are the only place a change would need to land:

1. **`POST /items/lost` response** is assumed to include the ranked matches
   in the same payload, so the results page can render immediately after
   submit without a second round trip:
   ```json
   {
     "item": { "id": "L-1234", "...": "..." },
     "matches": [
       {
         "id": "F-1042",
         "category": "Electronics",
         "description": "...",
         "image": "https://.../photo.jpg",
         "location": "...",
         "datetime": "2026-08-27T14:20:00",
         "finder_name": "...",
         "finder_email": "...",
         "finder_phone": "...",
         "final_score": 0.91
       }
     ]
   }
   ```
   If matching happens asynchronously (e.g. a background job), we'll need
   either a `GET /items/lost/{id}/matches` polling endpoint or a websocket —
   flagging this as a likely need once the real AI pipeline has real
   latency.

2. **`POST /items/found` response** is assumed to be `{ "item": { "id": ... } }`
   for the confirmation screen.

3. **Item Details** currently only opens from a match card (it's passed the
   full found-item object it already has in memory), since there's no
   endpoint to fetch a single found item by id. If we want the details page
   to be directly linkable/shareable, we'll need `GET /items/found/{id}`.

4. **Image field**: assumed to be uploaded as a `File` under the `image`
   key of the same multipart request as the rest of the form (not a
   separate upload endpoint). If images are meant to go to separate
   storage (e.g. presigned S3 URL) first, that's a different contract and
   `ImageUpload.jsx` / `client.js` will need to change together.

5. **Validation errors**: assumed FastAPI's default 422 shape
   (`{"detail": [{"loc": [...], "msg": "..."}]}`) and mapped to field-level
   errors automatically. If the real API returns something else, only
   `postForm()` in `client.js` needs updating.

## Design notes

Visual language is a "lost & found claim desk": ink-dark UI, kraft/brass
accents, a monospace "case file" register for data (ids, dates, scores),
and an ink-stamp motif for the match score — it visually "stamps" onto the
card when results land, which is the moment the whole demo hinges on.
