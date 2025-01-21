# myapp/myapp/after_install.py

import frappe

def set_accounts_settings():
    """
    Mengupdate Accounts Settings sesuai kebutuhan.
    """
    try:
        # Ambil dokumen Accounts Settings
        accounts_settings = frappe.get_doc("Accounts Settings")

        # Update nilai settings
        accounts_settings.update({
            "delete_linked_ledger_entries": 1,
            "check_supplier_invoice_uniqueness": 1,
            "enable_common_party_accounting": 1,
            "post_change_gl_entries": 0
        })

        # Simpan perubahan
        accounts_settings.save()
        frappe.db.commit()  # Commit perubahan ke database

        # Tampilkan pesan sukses
        frappe.msgprint("Accounts Settings berhasil diupdate setelah install.")

    except Exception as e:
        # Tangani error dan tampilkan pesan error
        frappe.log_error(f"Gagal mengupdate Accounts Settings: {str(e)}", "After Install Hook Error")
        frappe.throw("Terjadi kesalahan saat mengupdate Accounts Settings. Silakan cek log untuk detailnya.")

def set_selling_settings():
    """
    Mengupdate Selling Settings sesuai kebutuhan.
    """
    try:
        # Ambil dokumen Accounts Settings
        settings = frappe.get_doc("Selling Settings")

        # Update nilai settings
        settings.update({
            "territory": "Indonesia",
            "validate_selling_price": 1
        })

        # Simpan perubahan
        settings.save()
        frappe.db.commit()  # Commit perubahan ke database

        # Tampilkan pesan sukses
        frappe.msgprint("Selling Settings berhasil diupdate setelah install.")

    except Exception as e:
        # Tangani error dan tampilkan pesan error
        frappe.log_error(f"Gagal mengupdate Selling Settings: {str(e)}", "After Install Hook Error")
        frappe.throw("Terjadi kesalahan saat mengupdate Selling Settings. Silakan cek log untuk detailnya.")

def set_buying_settings():
    """
    Mengupdate Buying Settings sesuai kebutuhan.
    """
    try:
        # Ambil dokumen Accounts Settings
        settings = frappe.get_doc("Buying Settings")

        # Update nilai settings
        settings.update({
            "po_required": "Yes",
            "pr_required": "Yes"
        })

        # Simpan perubahan
        settings.save()
        frappe.db.commit()  # Commit perubahan ke database

        # Tampilkan pesan sukses
        frappe.msgprint("Buying Settings berhasil diupdate setelah install.")

    except Exception as e:
        # Tangani error dan tampilkan pesan error
        frappe.log_error(f"Gagal mengupdate Buying Settings: {str(e)}", "After Install Hook Error")
        frappe.throw("Terjadi kesalahan saat mengupdate Buying Settings. Silakan cek log untuk detailnya.")

def set_global_settings():
    """
    Mengupdate Global Settings sesuai kebutuhan.
    """
    try:
        # Ambil dokumen Accounts Settings
        settings = frappe.get_doc("Global Defaults")

        # Update nilai settings
        settings.update({
            "hide_currency_symbol": "No",
            "default_distance_unit": "Meter",
            "disable_in_words": 1
        })

        # Simpan perubahan
        settings.save()
        frappe.db.commit()  # Commit perubahan ke database

        # Tampilkan pesan sukses
        frappe.msgprint("Global Settings berhasil diupdate setelah install.")

    except Exception as e:
        # Tangani error dan tampilkan pesan error
        frappe.log_error(f"Gagal mengupdate Global Settings: {str(e)}", "After Install Hook Error")
        frappe.throw("Terjadi kesalahan saat mengupdate Global Settings. Silakan cek log untuk detailnya.")

def after_install():
    """
    Fungsi utama yang dijalankan setelah aplikasi diinstall.
    """
    print("🟡 Installed, Setting Up Apps...")

    set_accounts_settings()  # Panggil fungsi untuk mengatur Accounts Settings
    print("... ✅ Account Settings Installed")

    set_selling_settings()  # Panggil fungsi untuk mengatur Selling Settings
    print("... ✅ Selling Settings Installed")

    set_buying_settings()  # Panggil fungsi untuk mengatur Buying Settings
    print("... ✅ Buying Settings Installed")

    set_global_settings()  # Panggil fungsi untuk mengatur global Settings
    print("... ✅ Global Default Installed")

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