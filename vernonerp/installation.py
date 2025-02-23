import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
import subprocess

custom_fields = {
	"Sales Invoice": [
		{
			"fieldname": "no_resi",
			"label": "No Resi",
			"fieldtype": "Data",
			"insert_after": "po_no",  # po_no is the fieldname for Customer's Purchase Order
			"search_index": 1,
			"unique": 0
		},
		{
			"fieldname": "full_address",
			"label": "Full Address",
			"fieldtype": "Long Text",
			"insert_after": "customer_name",
		}
	],
	"Branch": [
		{
			"fieldname": "company",
			"label": "Company",
			"fieldtype": "Link",
			"options": "Company",
			"insert_after": "branch_name",
			"reqd": 1
		},
		{
			"fieldname": "Address",
			"label": "Address",
			"fieldtype": "Link",
			"options": "Address",
			"reqd": 1
		},
		{
			"fieldname": "contact",
			"label": "Contact",
			"fieldtype": "Link",
			"options": "Contact",
			"reqd": 1
		},
	]
}

settings_to_configure = {
	"System Settings": {
		"float_precision": 2,
		"currency_precision": 2,
		"allow_login_using_mobile_number": 1,
		"allow_login_using_user_name": 1,
		"deny_multiple_sessions": 1
	},
	"Accounts Settings": {
		"delete_linked_ledger_entries": 1,
		"check_supplier_invoice_uniqueness": 1,
		"enable_common_party_accounting": 1,
		"post_change_gl_entries": 0,
	},
	"Selling Settings": {
		"territory": "Indonesia",
		"validate_selling_price": 1,
	},
	"Buying Settings": {
		"po_required": "Yes",
		"pr_required": "Yes",
	},
	"Global Defaults": {
		"hide_currency_symbol": "No",
		"default_distance_unit": "Meter",
		"disable_in_words": 1,
	},
	"Print Settings": {
		"compact_item_print": 1,
		"print_uom_after_quantity": 1,
		"font": "Helvetica",
		"font_size": 9,
	}
}

item_groups = {
	"Products": "Uncategorized Products",
	"Services": "Uncategorized Services",
	"Consumables": "Uncategorized Consumables",
}


import frappe

def set_settings(setting_name, new_setting):
	"""
	Mengupdate {setting_name} dengan {new_setting} sesuai kebutuhan.
	"""
	try:
		# Ambil dokumen Accounts Settings
		settings = frappe.get_doc(setting_name)

		# Update nilai settings
		settings.update(new_setting)

		# Simpan perubahan
		settings.save()
		frappe.db.commit()  # Commit perubahan ke database

		# Tampilkan pesan sukses
		frappe.msgprint(f"{setting_name} Settings berhasil diupdate setelah install.")

	except Exception as e:
		# Tangani error dan tampilkan pesan error
		frappe.log_error(f"Gagal update: {str(e)}", "After Install Hook Error")
		frappe.throw(f"Terjadi kesalahan saat mengupdate {setting_name}. Error: {str(e)}.")

def setup_item_groups():
	# Definisi grup dan subgrup
	
	for group, sub_group in item_groups.items():
		# Periksa dan buat grup utama jika belum ada
		if not frappe.db.exists("Item Group", group):
			frappe.get_doc({
				"doctype": "Item Group",
				"item_group_name": group,
				"is_group": 1,  # Menjadikan ini grup
				"parent_item_group": "All Item Groups"  # Pastikan sesuai hierarki
			}).insert()
			print(f"....... ✅ Group '{group}' created.")
		else:
			# Jika grup sudah ada, pastikan diatur sebagai grup
			frappe.db.set_value("Item Group", group, "is_group", 1)
			print(f"....... ✅ Group '{group}' updated to be a group.")

		# Periksa dan buat subgrup jika belum ada
		if not frappe.db.exists("Item Group", sub_group):
			frappe.get_doc({
				"doctype": "Item Group",
				"item_group_name": sub_group,
				"is_group": 0,  # Subgrup bukan grup
				"parent_item_group": group  # Menghubungkan ke grup utama
			}).insert()
			print(f"....... ✅ Subgroup '{sub_group}' created under '{group}'.")
		else:
			print(f"....... ✅ Subgroup '{sub_group}' already exists under '{group}'.")

def create_default_outlets():
	"""Buat default Outlet untuk setiap Company"""
	companies = frappe.get_all("Company", fields=["name"])
	for company in companies:
		# Periksa apakah Outlet "Main" untuk perusahaan sudah ada
		if not frappe.db.exists("Outlet", {"outlet_name": "Main", "company": company["name"]}):
			outlet = frappe.get_doc({
					"doctype": "Outlet",
					"outlet_name": "Main",
					"description": f"Default Outlet for {company['name']}",
					"is_default": 1,
					"company": company["name"]
			})
			outlet.insert()
			frappe.db.commit()
			print(f"......✅ Default Outlet 'Main' created for Company '{company['name']}'.")
	else:
			print(f"......⚠️ Default Outlet 'Main' already exists for Company '{company['name']}'.")

def add_outlet_as_accounting_dimension():
	"""Tambahkan Outlet sebagai Accounting Dimension dan atur default serta mandatory settings"""
	# Periksa apakah Accounting Dimension untuk Outlet sudah ada
	accounting_dimension = frappe.db.get_value("Accounting Dimension", {"document_type": "Outlet"}, "name")
	if not accounting_dimension:
		# Buat Accounting Dimension baru untuk Outlet
		accounting_dimension = frappe.get_doc({
				"doctype": "Accounting Dimension",
				"document_type": "Outlet",
				"label": "Outlet",
				"disabled": 0  # Pastikan dimension aktif
		})
		print("✅...... Created new Accounting Dimension for Outlet.")
	else:
		accounting_dimension = frappe.get_doc("Accounting Dimension", accounting_dimension)
		print("⚠️...... Accounting Dimension for Outlet already exists, updating...")

	# Hapus semua entries di dimension defaults untuk memastikan tidak ada duplikasi
	accounting_dimension.dimension_defaults = []
	accounting_dimension.save()

	# Ambil semua perusahaan
	# companies = frappe.get_all("Company", fields=["name"])
	# for company in companies:
	# 	# Cari Outlet dengan is_default=1 untuk perusahaan tersebut
	# 	default_outlet = frappe.db.get_value("Outlet", {"company": company["name"], "is_default": 1}, "name")
	# 	if not default_outlet:
	# 			print(f"......⚠️ No default Outlet found for Company '{company['name']}', skipping.")
	# 			continue

	# 	# Tambahkan ke child table dimension_defaults
	# 	accounting_dimension.append("dimension_defaults", {
	# 			"company": company["name"],
	# 			"default_dimension": default_outlet,
	# 			"mandatory_for_bs": 1,  # Wajib untuk Balance Sheet
	# 			"mandatory_for_pl": 1  # Wajib untuk Profit and Loss
	# 	})
	# 	print(f"......✅ Added Company '{company['name']}' with default Outlet '{default_outlet}' to Accounting Dimension.")

	# Simpan perubahan
	accounting_dimension.save()
	frappe.db.commit()
	print("✅...... Accounting Dimension 'Outlet' updated successfully with mandatory settings.")

def add_brach_as_accounting_dimension():
	"""Tambahkan Branch sebagai Accounting Dimension dan atur default serta mandatory settings"""
	# Periksa apakah Accounting Dimension untuk Outlet sudah ada
	accounting_dimension = frappe.db.get_value("Accounting Dimension", {"document_type": "Branch"}, "name")
	if not accounting_dimension:
		# Buat Accounting Dimension baru untuk Outlet
		accounting_dimension = frappe.get_doc({
				"doctype": "Accounting Dimension",
				"document_type": "Branch",
				"label": "Branch",
				"disabled": 0  # Pastikan dimension aktif
		})
		print("✅...... Created new Accounting Dimension for Branch.")
	else:
		accounting_dimension = frappe.get_doc("Accounting Dimension", accounting_dimension)
		print("⚠️...... Accounting Dimension for Branch already exists, updating...")

	# Hapus semua entries di dimension defaults untuk memastikan tidak ada duplikasi
	accounting_dimension.dimension_defaults = []
	accounting_dimension.save()

	# Ambil semua perusahaan
	# companies = frappe.get_all("Company", fields=["name"])
	# for company in companies:
	# 	# Cari Outlet dengan is_default=1 untuk perusahaan tersebut
	# 	default_outlet = frappe.db.get_value("Outlet", {"company": company["name"], "is_default": 1}, "name")
	# 	if not default_outlet:
	# 			print(f"......⚠️ No default Outlet found for Company '{company['name']}', skipping.")
	# 			continue

	# 	# Tambahkan ke child table dimension_defaults
	# 	accounting_dimension.append("dimension_defaults", {
	# 			"company": company["name"],
	# 			"default_dimension": default_outlet,
	# 			"mandatory_for_bs": 1,  # Wajib untuk Balance Sheet
	# 			"mandatory_for_pl": 1  # Wajib untuk Profit and Loss
	# 	})
	# 	print(f"......✅ Added Company '{company['name']}' with default Outlet '{default_outlet}' to Accounting Dimension.")

	# Simpan perubahan
	accounting_dimension.save()
	frappe.db.commit()
	print("✅...... Accounting Dimension 'Outlet' updated successfully with mandatory settings.")


def after_install():
	"""
	Fungsi utama yang dijalankan setelah aplikasi diinstall.
	"""
	print("🟡 Installed, Setting Up Apps...")

	# ------------------------------------------------
	# Setup Settings
	# ------------------------------------------------
	for doctype, settings in settings_to_configure.items():
		set_settings(doctype, settings)
		print(f"... ✅ {doctype} Installed")

	# ------------------------------------------------
	# Setup Item Groups
	# ------------------------------------------------
	setup_item_groups()
	print(f"... ✅ Item Group Set")

	# ------------------------------------------------
	# Setup Sales Invoice
	# ------------------------------------------------
	create_custom_fields(custom_fields)
	try:
		doctype = "Sales Invoice"
		for field in custom_fields[doctype]:
			if not frappe.get_meta(doctype).get_field(field["fieldname"]):
				frappe.throw(f"Failed to create custom field: {field['fieldname']}")

		print(f"... ✅ Custom Fields Created")

	except Exception as e:
		frappe.log_error(f"Failed to create custom fields: {str(e)}", "Install Error")
		raise e

	# ------------------------------------------------
	# Add branch as Accounting DImension
	# ------------------------------------------------
	# create_default_outlets()
	add_brach_as_accounting_dimension()
	print(f"... ✅ Outlet has been added to Accounting Dimension")

def before_install():
	"""
	Fungsi yang dijalankan sebelum aplikasi diinstall.
	Memastikan ERPNext sudah terinstall.
	"""

	print("🟡 Installing, Checking up environment...")
	# Periksa apakah ERPNext sudah terinstal
	if not frappe.get_installed_apps() or "erpnext" not in frappe.get_installed_apps():
		frappe.throw("ERPNext harus diinstal sebelum Anda dapat menginstal aplikasi ini.")
	else:
		print("... ✅ ERPNext already installed")


# jalankan fungsi before uninstall
def before_uninstall():
	"""
	Fungsi yang dijalankan sebelum aplikasi diuninstall.
	"""
	print("🟡 Uninstalling, Checking up environment...")

	# Remove all custom_fields in the doctype of custom_fields
	for doctype, fields in custom_fields.items():
		for field in fields:
			# delete custom field if exists from doctype
			if frappe.get_meta(doctype).get_field(field["fieldname"]):
				frappe.delete_doc("Custom Field", field["fieldname"])
				print(f"... ✅ Custom Field {field['fieldname']} deleted")
			else:
				print(f"... ✅ Custom Field {field['fieldname']} not found")


			

