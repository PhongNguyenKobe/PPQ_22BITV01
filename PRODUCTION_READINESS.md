# CineAI production operations

## Database rollout

Back up PostgreSQL before rollout, then run:

```powershell
cd backend
python -m alembic upgrade head
```

The urgent migrations introduce per-seat tickets, combo inventory lifecycle,
checkout idempotency, pricing rules, promotion reservations, notification
outbox, and POS customer snapshots.

## Required production environment

```env
ENVIRONMENT=production
JWT_SECRET_KEY=<long-random-secret>
SHOWTIME_TURNAROUND_MINUTES=15
```

Changing `JWT_SECRET_KEY` invalidates existing signed ticket QR codes. Store it
in a secret manager and rotate it only with a planned ticket migration.

## Notification worker

Run this command on a schedule (for example every minute):

```powershell
cd backend
python scripts/process_notifications.py
```

The worker uses row locking, retries failed deliveries with backoff, and marks
an item failed after five attempts.

## Payment reconciliation

Payments in `RECONCILIATION_REQUIRED` must not issue tickets. Branch admins can
run reconciliation from the payments screen. A verified late VNPAY capture is
sent into the refund workflow automatically.

## Smoke-test checklist

1. Two accounts cannot reserve or buy the same seat.
2. Retrying with the same `Idempotency-Key` returns the same order/payment.
3. An expired booking restores reserved combo inventory.
4. A successful payment changes combo inventory from `RESERVED` to `SOLD`.
5. A multi-seat booking produces one signed QR per seat.
6. Tampered QR data is rejected and simultaneous scans consume a ticket once.
7. A late provider callback creates no ticket and requires reconciliation.
8. Promotion user limits, global quota, budget, branch/movie/date/payment rules are enforced.
9. POS cash sales are restricted to the employee's assigned branch.

## Remaining deployment work

Production infrastructure must provide centralized logs, metrics/alerts,
database backups with restore drills, TLS, rate limiting at the gateway, and a
managed scheduler/worker. These are deployment responsibilities and are not
created automatically by the application repository.
