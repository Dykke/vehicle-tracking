## 55% Change Scope Plan

This document defines the scoped changes targeting approximately 55% of the system. It balances new user-visible features and admin/driver tools while minimizing risk to existing code.

### Baseline (today)
- Auth with roles: `operator` and `commuter` via Flask-Login
- Commuter map (login required), vehicle list, live locations
- Operator dashboard with vehicle management and route selection (OSRM for distance)
- Socket-based live updates; `Vehicle` and `LocationLog` models

### Scope summary (adds up to 55%)

| Feature | Scope | % |
|---|---|---|
| Public user map (view-only) | Make commuter map public; read-only data; no login | 5 |
| Vehicle vacancy/full in popup | Add `occupancy_status` or `seats_available`; show on click | 3 |
| Public ETA (no account) | OSRM route distance + recent speed to destination | 6 |
| Driver password change | Allow password update; lock username | 1 |
| Driver action logs | Log vacancy/full toggles and key actions | 5 |
| Passenger in/out logs | Trip + events (board/alight) with timestamps | 6 |
| Driver profile picture (admin-only) | Store/display only in admin | 2 |
| Routing confirm and abort | Confirm dialog; abort to clear active routing | 2 |
| Centralized admin console | Admin role; global fleet view and logs | 7 |
| Activate/deactivate driver + archive access | `is_active` flag; prevent login; keep logs | 3 |
| OTP for admin | TOTP during admin login | 3 |
| Terms/Policy updates | Clarify visibility/consent | 1 |
| ETA accuracy improvements | Speed smoothing + GPS accuracy thresholds | 4 |
| Driver photo capture; admin-reviewed verification | 7 |
|  |  | **55** |


---

### Milestones and validations

#### M1: Public map and vehicle details (14%)
- Public map route (remove `@login_required` for public endpoint) and read-only APIs
- Vehicle popup shows `occupancy_status` or `seats_available`
- Public ETA endpoint computes ETA from vehicle → user-selected destination

Validation
- Open map in incognito; vehicles render without login
- Click a vehicle; popup shows status and computed ETA
- Compare ETA vs OSRM distance/current speed on 3 samples (<±20% error)

#### M2: Driver UX and logging (14%)
- Password change (no username change)
- Driver action logs on vacancy/full toggles and route actions
- Routing confirm/abort before starting navigation

Validation
- Change password; old fails, new works
- Toggle status twice; two log entries with timestamps appear in admin logs
- Confirm route prompts; abort clears route state

#### M3: Passenger events and trips (12%)
- `Trip` lifecycle (start/end)
- `PassengerEvent` records board/alight counts with timestamps

Validation
- Start a trip; record multiple board/alight; totals reconcile; timestamps ordered
- End trip; trip summary retained and visible in admin logs

#### M4: Admin console, activation, OTP, profile pics (15%)
- Admin role and console for fleet + logs
- Activate/deactivate drivers (`is_active`) with archived logs retained
- OTP (TOTP) for admin login
- Driver profile image upload (visible only to admin)

Validation
- Admin can view all vehicles/logs; non-admin cannot
- Deactivated driver can’t log in; historical logs still viewable by admin
- OTP required for admin; invalid code blocked
- Profile image appears only in admin UI

#### M5: Policy and accuracy (5%)
- Update Terms/Privacy to state potential public visibility of vehicle and trip metadata
- Improve ETA: speed smoothing from recent `LocationLog` samples; ignore low-accuracy GPS

Validation
- Terms modal/page updated; admin and driver see updates; public banner displayed once
- ETA error improves on test runs (<±15% on 5 samples)

---

### Data model updates

- Table: `users`
  - Add: `role` may include `admin` (reuse `user_type` or expand values)
  - Add: `is_active` (bool, default true)
  - Add: `profile_image_url` (string, nullable)

- Table: `vehicles`
  - Add: `occupancy_status` (enum: `vacant`|`full`) or `seats_available` (int)
  - Add: `last_speed_kmh` (float, nullable) – optional derived cache

- New table: `driver_action_logs`
  - `id`, `driver_id`, `vehicle_id`, `action` (string), `metadata` (JSON), `created_at`

- New table: `trips`
  - `id`, `vehicle_id`, `driver_id`, `route_name`, `start_time`, `end_time`, `status`

- New table: `passenger_events`
  - `id`, `trip_id`, `event_type` (`board`|`alight`), `count`, `created_at`, `notes`

Indexes
- Index `driver_action_logs.vehicle_id`, `trips.vehicle_id`, and `passenger_events.trip_id`

---

### API surface (proposed)

Public
- GET `/public/vehicles/active` – list vehicles (subset of `/api/vehicles/active`), no PII
- GET `/public/vehicle/<id>/eta?dest=<place or lat,lng>` – compute ETA via OSRM + recent speed

Driver
- POST `/driver/vehicle/<id>/occupancy` – set vacancy/full or seats remaining (logs action)
- POST `/driver/trip/start` – create trip for a vehicle
- POST `/driver/trip/end` – end current trip
- POST `/driver/passenger` – record board/alight `{type, count, note?}`
- POST `/driver/password` – change password (current + new)

Admin
- GET `/admin/logs/actions` – filterable driver action logs
- GET `/admin/trips` – list trips and passenger summaries
- POST `/admin/driver/<id>/activate` / `/deactivate`
- Admin login with OTP (TOTP) – applies to `/login` when role is `admin`

---

### UI updates

Public (no login)
- Map page shows vehicles, popup with vacancy/full, destination picker for ETA

Driver
- Status toggle with confirmation; abort route; passenger board/alight quick actions
- Settings: change password; profile image upload (driver cannot see other drivers)

Admin
- Fleet overview (all vehicles, routes, statuses)
- Logs and trip summaries; driver profile images; activate/deactivate toggle

---

### Risk and privacy controls
- Public endpoints must exclude any PII
- Clarify in Terms that trip metadata may be visible publicly in aggregate

---

### Rollout and testing
- Deploy per milestone; run DB migrations with backups
- Track error rate and ETA accuracy metrics after M1 and M5
- Add feature flags where practical (public map, OTP requirement)

---

### Acceptance criteria (high-level)
- Public can view vehicles and ETA without account
- Drivers can log actions and passenger counts with audit trail
- Admin can centrally monitor, activate/deactivate, and requires OTP
- ETA reasonably accurate (<±15% on test set) and improves with movement
