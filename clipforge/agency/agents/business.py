"""Business agent: turns won leads into clients, delivers finished orders and invoices them."""
import os

from .. import config, db
from .base import Agent

TERMINAL = ("scheduled", "rejected", "qc_failed")
OVERDUE_DAYS = float(os.getenv("CLIPFORGE_OVERDUE_DAYS", "14"))


class BusinessAgent(Agent):
    name = "business"
    role = "Clients, orders, payments and delivery"

    def step(self) -> bool:
        return self._convert_won_leads() or self._deliver_orders() or self._flag_overdue()

    def _convert_won_leads(self) -> bool:
        lead = db.row("SELECT * FROM leads WHERE stage = 'won' AND id NOT IN "
                      "(SELECT lead_id FROM clients WHERE lead_id IS NOT NULL) LIMIT 1")
        if not lead:
            return False
        self.working(f"Onboarding {lead['name']} as a client")
        cid = db.insert("clients", name=lead["name"], email=lead.get("email"), package="starter",
                        status="active", lead_id=lead["id"])
        self.log(f"New client: {lead['name']} (from lead #{lead['id']})", entity=("client", cid))
        self.done()
        return True

    def _deliver_orders(self) -> bool:
        for order in db.rows("SELECT * FROM orders WHERE status = 'in_production'"):
            clips = db.rows("SELECT status FROM clips WHERE order_id = ?", (order["id"],))
            if not clips or any(c["status"] not in TERMINAL for c in clips):
                continue
            oid = order["id"]
            self.working(f"Closing out order #{oid}")
            delivered = sum(c["status"] == "scheduled" for c in clips)
            if delivered == 0:
                db.update("orders", oid, status="needs_attention", error="No clips were approved")
                self.log(f"Order #{oid}: no approved clips. Needs your attention", "warn", ("order", oid))
                return True
            db.update("orders", oid, status="delivered", delivered_at=db.now())
            if not db.row("SELECT id FROM invoices WHERE order_id = ?", (oid,)):
                iid = db.insert("invoices", client_id=order["client_id"], order_id=oid,
                                amount_cents=order["price_cents"], status="sent")
                self.log(f"Order #{oid} delivered ({delivered}/{len(clips)} clips). "
                         f"Invoice #{iid} for ${order['price_cents'] / 100:,.2f} sent", entity=("invoice", iid))
            self.done()
            return True
        return False

    def _flag_overdue(self) -> bool:
        cutoff = db.now() - OVERDUE_DAYS * 86400
        inv = db.row("SELECT * FROM invoices WHERE status = 'sent' AND created_at < ? LIMIT 1", (cutoff,))
        if not inv:
            return False
        db.update("invoices", inv["id"], status="overdue")
        self.log(f"Invoice #{inv['id']} is overdue", "warn", ("invoice", inv["id"]))
        return True


def price_for(package: str) -> tuple[int, int]:
    return config.PACKAGES.get(package, config.PACKAGES["starter"])
