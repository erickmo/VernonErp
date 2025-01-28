import frappe
from frappe.utils import nowdate, flt

def execute():
	# Ambil semua data Wallet Shopee yang belum diproses
	wallet_shopee_list = frappe.get_all("Wallet Shopee",
		filters={
			"payment_entry": ["is", "not set"],
			"journal_entry": ["is", "not set"],
			# "no_pesanan": "2412282WPN11F6",
		},
		fields=["*"]
	)

	for x in wallet_shopee_list:
		try:
			if x.no_pesanan != "-":
				# 2.1. Buat Payment Entry untuk Sales Invoice yang sesuai
				# print(f"Processing Payment Entry {x.no_pesanan}")
				create_payment_entry(x)
				print(f"...✅ {x.name} telah diproses Payment Entrynya")
			else:
				# 2.2. Buat Journal Entry
				# print(f"Processing Journal Entry {x.tanggal_pesanan}")
				create_journal_entry(x)
				print(f"...✅ {x.name} telah dibuat Journal Entrynya")

		except Exception as e:
			frappe.log_error(f"Gagal memproses Wallet Shopee {x.name}: {str(e)}")
			print(f"❌❌ Gagal memproses Wallet Shopee {x.name}: {str(e)}")

def create_payment_entry(x):
	# Cari Sales Invoice berdasarkan no_pesanan
	sinv = frappe.get_doc("Sales Invoice", {"po_no": x.no_pesanan})
	if not sinv:
		frappe.throw(f"Sales Invoice dengan PO No {x.no_pesanan} tidak ditemukan.")
	if sinv.docstatus == 0:
		frappe.throw(f"Sales Invoice dengan PO No {x.no_pesanan} belum tersubmit.")
	if sinv.docstatus == 2:
		frappe.throw(f"Sales Invoice dengan PO No {x.no_pesanan} telah dicancel.")

	# Buat Payment Entry
	payment_entry = frappe.new_doc("Payment Entry")
	payment_entry.payment_type = "Receive"
	payment_entry.posting_date = x.tanggal_transaksi
	payment_entry.party_type = "Customer"
	payment_entry.party = sinv.customer
	payment_entry.paid_from = sinv.debit_to
	payment_entry.paid_to = x.wallet_account
	payment_entry.paid_to_account_currency = sinv.currency
	payment_entry.target_exchange_rate = 1
	payment_entry.paid_amount = flt(x.jumlah)
	payment_entry.received_amount = flt(x.jumlah)
	payment_entry.append("references", {
		"reference_doctype": "Sales Invoice",
		"reference_name": sinv.name,
		"total_amount": flt(x.jumlah),
		"outstanding_amount": flt(x.jumlah),
		"allocated_amount": flt(x.jumlah)
	})

	payment_entry.save()
	payment_entry.submit()

	# Update Wallet Shopee dengan Sales Invoice dan Payment Entry
	wallet_shopee = frappe.get_doc("Wallet Shopee", x.name)
	wallet_shopee.payment_entry = payment_entry.name
	wallet_shopee.save()
	frappe.db.commit()

def create_journal_entry(x):
	# Buat Journal Entry
	journal_entry = frappe.new_doc("Journal Entry")
	journal_entry.posting_date = x.tanggal_transaksi
	journal_entry.voucher_type = "Journal Entry"
	journal_entry.company = x.company  # Sesuaikan dengan perusahaan Anda

	# Detail Journal Entry
	if flt(x.jumlah) > 0:
		journal_entry.append("accounts", {
			"account": x.wallet_account,
			"debit_in_account_currency": flt(x.jumlah),
			"credit_in_account_currency": 0
		})
		journal_entry.append("accounts", {
			"account": x.balancing_account,
			"debit_in_account_currency": 0,
			"credit_in_account_currency": flt(x.jumlah)
		})
	else:
		journal_entry.append("accounts", {
			"account": x.wallet_account,
			"debit_in_account_currency": 0,
			"credit_in_account_currency": abs(flt(x.jumlah))
		})
		journal_entry.append("accounts", {
			"account": x.balancing_account,
			"debit_in_account_currency": abs(flt(x.jumlah)),
			"credit_in_account_currency": 0
		})

	journal_entry.insert()

	# Update Wallet Shopee dengan Journal Entry
	frappe.db.set_value("Wallet Shopee", x.name, {
		"journal_entry": journal_entry.name
	})
	frappe.db.commit()
