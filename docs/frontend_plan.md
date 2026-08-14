# Moodify Frontend Plan (React + Vite)

**Purpose:** the working reference for building the React frontend. **Read this at the start of every frontend session** to see where we are and what's next. This is the *actionable build plan + live status*; `project_spec.md` Section 24 holds the deeper *rationale*. If the two ever disagree, fix the docs — status must match the code.

**How to resume a session:** "Read `docs/frontend_plan.md`, tell me the current phase and the next task, then let's continue."

---

## 1. Why we're building this (goal alignment)

The React frontend is **Priority 1** of the SWE pivot. The product currently has an API + a Streamlit dashboard, which is not a real product UI. To a SWE interviewer, "I built a Streamlit data app" and "I built a React frontend against my own REST API" test completely different skills. This is the single highest-leverage gap.

Overriding constraint: **Nathan must be able to defend every decision in an interview.** No vibe coding. Each step below produces something running that Nathan fully understands. Claude teaches the *why*; Nathan owns the reasoning.

---

## 2. Locked decisions (and the one-line defense for each)

| Decision | Choice | Defense (know this cold) |
|---|---|---|
| Framework | **React + Vite** (not Next.js) | Focus is component architecture, hooks, client/server data flow — not SSR/file-routing. Next.js is a later story, not an intern-level requirement. |
| Language | **TypeScript** | Types mirror the backend's Pydantic schemas, making the client/server contract explicit and self-documenting. Near table-stakes at startups/consumer tech. |
| Styling | **CSS Modules** | Scoped styles, zero magic, no extra dependency. Keeps focus on React itself; trivial to defend. |
| State | **Built-in `useState` / `useContext`** (not Redux) | State surface is small (query, results, later auth session). Knowing *when not* to reach for Redux is the signal. |
| Data fetching | **Plain `fetch`** (not React Query yet) | Learn the loading/error/success state machine by hand once before a library hides it. React Query is a reasonable later story. |
| Routing | **`react-router`** | Added in Phase 3, once there's more than one page (results / login / history). Not in the first slice. |
| MVP auth | **Relax `X-API-Key` on `/recommend/*`** for now | A SPA has no server to hide a key in; shipping a key to the browser violates our own security rule. A/B group is already hardcoded to `"A"`, so nothing is lost. Real per-user auth (JWT) is Priority 2 and replaces this. |

**Guiding method:** build in **vertical slices** — thinnest end-to-end path first (one input → one API call → results on screen), then thicken. Never build all components, then all fetching, then wire.

---

## 3. Build order (phases)

Status keys: ⬜ not started · 🟡 in progress · ✅ done

### Phase 0 — Walking skeleton ⬜
Goal: the two servers talk; nothing rendered yet.
- [ ] Create feature branch (`feature/react-frontend`)
- [ ] Scaffold Vite React + TS in `frontend-react/`
- [ ] Add `CORSMiddleware` to FastAPI (allow `http://localhost:5173`)
- [ ] Relax `X-API-Key` on `/recommend/track` and `/recommend/mood` (temporary — see §9)
- [ ] Prove one real call works (log `/health` or `/search/tracks` JSON to console)
- **Done when:** Vite dev server runs and a real fetch to the backend returns data with no CORS error.

### Phase 1 — One endpoint, by hand ⬜
Goal: the core learning step — the manual data-fetching state machine.
- [ ] `src/api/` client module (typed `fetch` wrapper, base URL from env)
- [ ] `src/types/` TS interfaces mirroring the API (see §6)
- [ ] One view that calls `POST /recommend/mood` and renders raw results
- [ ] Explicit `loading` / `error` / `data` state with `useState`
- **Done when:** typing a mood returns 10 tracks on screen, with visible loading and error states.

### Phase 2 — The real UX ⬜
Goal: rebuild the Streamlit flow as real components.
- [ ] Mood / Track mode toggle
- [ ] `SearchBar` — track autocomplete via `GET /search/tracks` → dropdown → pick
- [ ] `SongCard` list + `ExplanationText` (must handle `explanation: null` gracefully — see §5)
- [ ] Similarity score display
- **Done when:** both mood and track flows work end-to-end and look like a product, not a form.

### Phase 3 — Routing ⬜
- [ ] Add `react-router`; split into pages once a second page exists
- **Done when:** navigation works between at least two pages.

### Later — Auth & history (Priority 2, not now) ⬜
- Login / signup pages, nav reflecting auth state, history page. Depends on the backend auth work (`project_spec.md` Section 25). **Do not start until Phases 0–3 are solid.**

---

## 4. Target structure (`frontend-react/`)

Proposed — adjust as it grows:

```
frontend-react/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── src/
    ├── main.tsx              # React entry
    ├── App.tsx              # top-level container / layout
    ├── api/
    │   └── client.ts        # typed fetch wrapper, base URL from env, error handling
    ├── types/
    │   └── api.ts           # TS interfaces mirroring backend schemas (§6)
    ├── components/          # presentational, one component per file
    │   ├── SearchBar/
    │   ├── SongCard/
    │   └── ExplanationText/
    └── pages/               # added in Phase 3 with react-router
```

Style rule (from `overview.md`): functional components + hooks only, one component per file, keep components presentational; data fetching lives in `src/api`, not scattered inline.

---

## 5. Backend API the frontend consumes (exact, as currently built)

Base URL (local): `http://localhost:8000`. These are the **only 4 live endpoints** — everything else in `project_spec.md` Section 6 is planned, not built.

### `GET /health` — no auth
```json
{ "status": "ok", "db": "connected" }
```
(Returns `{"status": "degraded", "db": "unreachable"}` if the DB is down. Note: this is the *real* shape — the `catalog_size`/`index_loaded` shape in the spec was never implemented.)

### `GET /search/tracks?q=<1–100 chars>` — no auth, 30/min
```json
{ "results": [ { "spotify_id": "…", "name": "…", "artist": "…", "album": "… | null" } ] }
```
Up to 10 matches on name OR artist, popularity-ordered. `422` if `q` empty or >100 chars.

### `POST /recommend/track` — auth (being relaxed for MVP), 10/min
Request: `{ "spotify_id": "…", "limit": 10 }` (`limit` 1–50)
Response: `RecommendationResponse` (below). **`explanation` is always `null` for track mode** — explanations are only generated for mood. `404` if `spotify_id` not in catalog.

### `POST /recommend/mood` — auth (being relaxed for MVP), 10/min
Request: `{ "mood_string": "…", "limit": 10 }` (`mood_string` 1–500 chars)
Response: `RecommendationResponse`. `explanation` is populated, but **can be `null`** if the Claude explanation call fails (the request still succeeds). `422` if mood empty or >500 chars.

### `RecommendationResponse` envelope (both recommend endpoints)
```json
{
  "recommendations": [
    {
      "spotify_id": "string",
      "name": "string",
      "artist": "string",
      "album": "string | null",
      "explanation": "string | null",
      "similarity_score": 0.94
    }
  ],
  "experiment_group": "A",
  "strategy": "cosine_similarity",
  "log_id": 142
}
```

**Frontend implication:** the `SongCard` must render cleanly when `album` and/or `explanation` are `null`. Track mode never has explanations; mood mode usually does. Don't assume they're present.

---

## 6. TypeScript types to create (mirror the Pydantic schemas)

```ts
// src/types/api.ts
export interface TrackSearchResult {
  spotify_id: string;
  name: string;
  artist: string;
  album: string | null;
}
export interface TrackSearchResponse {
  results: TrackSearchResult[];
}
export interface TrackRecommendation {
  spotify_id: string;
  name: string;
  artist: string;
  album: string | null;
  explanation: string | null;
  similarity_score: number;
}
export interface RecommendationResponse {
  recommendations: TrackRecommendation[];
  experiment_group: string;
  strategy: string;
  log_id: number;
}
```

Interview point: these types are the *contract*. If the backend schema changes, the TS compiler catches the mismatch at build time — that's the payoff of choosing TypeScript.

---

## 7. Components & pages (from Section 24)

- **SearchBar** — mood text input + track autocomplete (dropdown of `/search/tracks` matches). Presentational; lifts the selected value up.
- **SongCard** — one recommendation: name, artist, album, similarity score, explanation (nullable), later feedback buttons.
- **ExplanationText** — renders the Claude explanation or a graceful fallback when null.
- **Results list / container** — owns the fetch + loading/error/data state, maps results to `SongCard`s.
- **Nav bar** — reflects auth state (Priority 2).
- **Pages** (Phase 3+): Mood/Track search, Results, Login/Signup, History.

Container vs presentational: one container owns data + state; the rest just render props. Be able to name which is which and why.

---

## 8. Interview-defensibility checkpoints

By the time the frontend is done, Nathan should be able to explain, without notes:
- The **loading / error / success state machine** built by hand, and why we did it before reaching for React Query.
- Why **built-in state**, not Redux, at this scale.
- **Client/server data flow** and why **CORS** is required (browser security model, not a FastAPI quirk).
- The **API-key-in-a-SPA tension**: a SPA can't hide a secret, which is *why* real user auth (JWT) is the next priority — a clean segue in an interview.
- Why **CSS Modules** (scoping) over global CSS.
- How **TypeScript types mirror the Pydantic schemas** and catch contract drift at build time.
- At least one **rendering/performance decision** (e.g. keys, memoization, debouncing the search box).

---

## 9. Backend changes this milestone requires (track these)

- [ ] **CORS** — add `CORSMiddleware` allowing the Vite dev origin (`http://localhost:5173`). Needed before any browser call works.
- [ ] **Relax `X-API-Key`** on `/recommend/track` and `/recommend/mood` — temporary for the MVP. **Revert / replace with JWT auth when Priority 2 lands.** Leave a comment in `main.py` so it isn't forgotten.
- [ ] (Priority 2, later) `/auth/*` endpoints, `users` table, nullable `user_id` on logs/feedback.

---

## 10. Definition of done (Section 24)

The React frontend fully replaces Streamlit as the product-facing entry point, is deployed, and calls the existing FastAPI endpoints (plus the new auth endpoints once built). Nathan can explain the component structure, the state flow, and at least one rendering/performance decision without notes.

---

## 11. Current status

- **Phase:** Phase 0 — not started.
- **Decisions:** all locked (see §2).
- **Next action:** create `feature/react-frontend` branch, scaffold Vite React+TS in `frontend-react/`, add CORS, relax auth on `/recommend/*`, prove one call works.
- **`frontend-react/` exists?** No — not yet scaffolded.

_Update this section at the end of every frontend session (mirror the same status into `CLAUDE.md` Current Status)._
