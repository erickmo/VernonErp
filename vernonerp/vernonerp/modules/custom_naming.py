import frappe
from frappe.model.naming import make_autoname

def set_naming(doc, method):
		# Cek apakah dokumen adalah return
		is_return = getattr(doc, "is_return", 0)  # Ambil nilai field is_return (default = 0)

		# Tentukan kode dokumen berdasarkan tipe
		if doc.doctype == "Purchase Invoice":
				document_code = "PIR" if is_return else "PINV"
		elif doc.doctype == "Sales Invoice":
				document_code = "SIR" if is_return else "SINV"
		else:
				frappe.throw(f"Custom naming not defined for {doc.doctype}")

		# Ambil tahun dan bulan dari posting_date
		if not doc.posting_date:
				frappe.throw("Posting Date is required to generate the document number.")

		year_month = doc.posting_date.strftime("%Y%m")  # Format YYYYMM

		# Buat format nomor dokumen
		doc.name = make_autoname(f"{document_code}-{year_month}-.#####")