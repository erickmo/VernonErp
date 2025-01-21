import frappe
from frappe.model.naming import make_autoname
from frappe import _

# Mapping doctype ke kode dan field return yang sesuai
DOCTYPE_SETTINGS = {
    "Sales Invoice": {
        "code": "SINV",
        "return_field": "is_return",
        "date_field": "posting_date"
    },
    "Purchase Invoice": {
        "code": "PINV",
        "return_field": "is_return",
        "date_field": "posting_date"
    },
    "Delivery Note": {
        "code": "DN",
        "date_field": "posting_date"
    },
    "Sales Order": {
        "code": "SO",
        "date_field": "transaction_date"
    },
    "Purchase Order": {
        "code": "PO",
        "date_field": "transaction_date"
    },
    "Payment Entry": {
        "code": "PAY",
        "date_field": "posting_date"
    },
    "Journal Entry": {
        "code": "ACCJE",
        "date_field": "posting_date"
    }
}

def autoname(doc, method):
    """
    Custom autoname untuk doctype yang memiliki transaction_date atau posting_date
    Format: {doc_code}-YYYYMM-xxxxx
    """
    try:
        settings = DOCTYPE_SETTINGS.get(doc.doctype)
        
        if not settings:
            # Jika tidak ada di mapping, gunakan autoname default
            doc.name = make_autoname(doc.autoname or "hash")
            return

        # 1. Tentukan doc_code
        doc_code = settings["code"]
        if settings.get("return_field") and doc.get(settings["return_field"]):
            doc_code += "R"

        # 2. Ambil tanggal yang sesuai
        date_field = settings["date_field"]
        date = doc.get(date_field)
        
        if not date:
            frappe.throw(_("{0} tidak boleh kosong").format(
                doc.meta.get_label(date_field)
            ))

        # 3. Format tanggal ke YYYYMM
        year_month = date.strftime("%Y%m")

        # 4. Buat series pattern
        series_pattern = f"{doc_code}-{year_month}-.#####"
        
        # 5. Generate autoname
        doc.name = make_autoname(series_pattern)

    except Exception as e:
        frappe.log_error(_("Gagal generate autoname untuk {0} {1}").format(
            doc.doctype, doc.name
        ))
        frappe.throw(_("Terjadi kesalahan dalam generate nomor dokumen. Silakan coba lagi."))