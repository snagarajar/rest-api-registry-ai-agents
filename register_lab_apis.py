"""Run this once to pre-register lab app APIs into the registry."""
import requests

BASE = "http://localhost:9000/registry/register"

APIS = [
    {
        "name": "List Lab Orders",
        "description": "List all lab orders from LIMS. Filter by status: received/processing/completed/cancelled",
        "endpoint": "http://localhost:8500/lab/orders",
        "method": "GET",
        "parameters": ["status"],
        "owner_team": "Lab LIMS",
        "auth_type": "none",
        "dependencies": [],
    },
    {
        "name": "Create Lab Order",
        "description": (
            "Create a new lab order. Required fields: sample_type, sample_count, assay, requester. "
            "Optional: priority (urgent/normal/low), notes"
        ),
        "endpoint": "http://localhost:8500/lab/orders",
        "method": "POST",
        "parameters": ["sample_type", "sample_count", "assay", "requester", "priority", "notes"],
        "owner_team": "Lab LIMS",
        "auth_type": "none",
        "dependencies": [],
    },
    {
        "name": "Update Order Status",
        "description": "Update a lab order status to received, processing, completed, or cancelled",
        "endpoint": "http://localhost:8500/lab/orders/{order_id}/status",
        "method": "PATCH",
        "parameters": ["order_id", "status"],
        "owner_team": "Lab LIMS",
        "auth_type": "none",
        "dependencies": [],
    },
    {
        "name": "List Inventory",
        "description": "List all lab inventory items. Filter by category (reagent/equipment/consumable) or low_stock=true",
        "endpoint": "http://localhost:8500/lab/inventory",
        "method": "GET",
        "parameters": ["category", "low_stock"],
        "owner_team": "Lab Inventory",
        "auth_type": "none",
        "dependencies": [],
    },
    {
        "name": "Consume Inventory Item",
        "description": "Reduce lab inventory quantity for an item used in an experiment",
        "endpoint": "http://localhost:8500/lab/inventory/{item_id}/consume",
        "method": "POST",
        "parameters": ["item_id", "quantity", "reason"],
        "owner_team": "Lab Inventory",
        "auth_type": "none",
        "dependencies": [],
    },
    {
        "name": "Restock Inventory Item",
        "description": "Increase lab inventory quantity when new stock arrives",
        "endpoint": "http://localhost:8500/lab/inventory/{item_id}/restock",
        "method": "POST",
        "parameters": ["item_id", "quantity", "reason"],
        "owner_team": "Lab Inventory",
        "auth_type": "none",
        "dependencies": [],
    },
    {
        "name": "List Invoices",
        "description": "List all finance invoices. Filter by status: pending/paid/overdue/cancelled",
        "endpoint": "http://localhost:8500/lab/finance",
        "method": "GET",
        "parameters": ["status"],
        "owner_team": "Finance",
        "auth_type": "none",
        "dependencies": [],
    },
    {
        "name": "Mark Invoice Paid",
        "description": "Mark a finance invoice as paid by invoice ID (e.g. INV-001)",
        "endpoint": "http://localhost:8500/lab/finance/{invoice_id}/pay",
        "method": "PATCH",
        "parameters": ["invoice_id"],
        "owner_team": "Finance",
        "auth_type": "none",
        "dependencies": [],
    },
    {
        "name": "List Products",
        "description": "List all products in the catalog. Filter by category or status (active/discontinued/beta)",
        "endpoint": "http://localhost:8500/lab/products",
        "method": "GET",
        "parameters": ["category", "status"],
        "owner_team": "Products",
        "auth_type": "none",
        "dependencies": [],
    },
]

if __name__ == "__main__":
    for api in APIS:
        r = requests.post(BASE, json=api)
        d = r.json()
        print(f"[{r.status_code}] {d.get('api_id','ERR')} — {api['name']}")
    print(f"\nDone — registered {len(APIS)} APIs.")
    print("\n--- 2 APIs left for YOU to register via http://localhost:9000/registry-ui ---")
    print("1. Create Invoice  | POST  | http://localhost:8500/lab/finance")
    print("   Params: client, amount, description, due_date, currency | Team: Finance")
    print("")
    print("2. Create Product  | POST  | http://localhost:8500/lab/products")
    print("   Params: name, category, version, price, description | Team: Products")
