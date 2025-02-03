import frappe
from frappe.utils import flt, nowdate

def process_wallet_tokopedia():
    # 1. Ambil semua data dari Wallet Tokopedia yang journal_entry dan payment_entry belum terisi, urutkan berdasarkan tanggal
    wallet_entries = frappe.get_all("Wallet Tokopedia",
                                    filters={"journal_entry": ["is", "not set"], 
                                             "payment_entry": ["is", "not set"]},
                                    fields=["name", "date", "description", "tipe_transaksi", 
                                            "no_pesanan", "nominal", "wallet_account", 
                                            "balancing_account"],
                                    order_by="date asc")

    for x in wallet_entries:
        # 2. Loop setiap entry dan proses sesuai tipe transaksi
        if x.tipe_transaksi == "payment":
            create_payment_entry(x)
        else:
            create_journal_entry(x)

def create_payment_entry(x):
    """Membuat Payment Entry atas Sales Invoice (sinv) dengan sinv.po_no = x.no_pesanan"""
    sinv = frappe.get_value("Sales Invoice", {"po_no": x.no_pesanan}, "name")

    if not sinv:
        frappe.log_error(f"Sales Invoice dengan PO No {x.no_pesanan} tidak ditemukan", "Payment Entry Error")
        return
    
    payment_entry = frappe.new_doc("Payment Entry")
    payment_entry.payment_type = "Receive"
    payment_entry.posting_date = x.date
    payment_entry.party_type = "Customer"
    payment_entry.party = frappe.get_value("Sales Invoice", sinv, "customer")
    payment_entry.paid_from = frappe.get_value("Sales Invoice", sinv, "debit_to")
    payment_entry.paid_to = x.wallet_account
    payment_entry.paid_amount = flt(x.nominal)
    payment_entry.received_amount = flt(x.nominal)

    payment_entry.append("references", {
        "reference_doctype": "Sales Invoice",
        "reference_name": sinv,
        "total_amount": flt(x.nominal),
        "outstanding_amount": flt(x.nominal),
        "allocated_amount": flt(x.nominal)
    })

    payment_entry.insert(ignore_permissions=True)

    # Update Wallet Tokopedia dengan Payment Entry yang baru
    frappe.db.set_value("Wallet Tokopedia", x.name, "payment_entry", payment_entry.name)
    frappe.db.commit()

    # Submit Payment Entry setelah diupdate ke Wallet Tokopedia
    payment_entry.submit()

def create_journal_entry(x):
    """Membuat Journal Entry dengan debit ke balancing_account dan credit ke wallet_account"""
    je = frappe.new_doc("Journal Entry")
    je.posting_date = x.date
    je.voucher_type = "Journal Entry"
    je.company = frappe.defaults.get_defaults().get("company")
    je.user_remark = f"{x.date} - {x.description}"  # Tambahkan user_remark dengan tanggal & deskripsi

    # Debit Entry
    je.append("accounts", {
        "account": x.balancing_account,
        "debit_in_account_currency": abs(flt(x.nominal))
    })

    # Credit Entry
    je.append("accounts", {
        "account": x.wallet_account,
        "credit_in_account_currency": abs(flt(x.nominal))
    })

    je.insert(ignore_permissions=True)

    # Update Wallet Tokopedia dengan Journal Entry yang baru
    frappe.db.set_value("Wallet Tokopedia", x.name, "journal_entry", je.name)
    frappe.db.commit()