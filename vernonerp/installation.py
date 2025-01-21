# myapp/myapp/after_install.py

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
    item_groups = {
        "Products": "Uncategorized Products",
        "Services": "Uncategorized Services",
        "Consumables": "Uncategorized Consumables",
    }

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

def after_install():
    """
    Fungsi utama yang dijalankan setelah aplikasi diinstall.
    """
    print("🟡 Installed, Setting Up Apps...")

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

    for doctype, settings in settings_to_configure.items():
        set_settings(doctype, settings)
        print(f"... ✅ {doctype} Installed")

    setup_item_groups()
    print(f"... ✅ Item Group Set")

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