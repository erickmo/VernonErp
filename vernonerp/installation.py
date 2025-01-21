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

def set_other_settings():
    """
    Fungsi untuk mengatur settings lainnya.
    """
    try:
        # Contoh: Update System Settings
        system_settings = frappe.get_doc("System Settings")
        system_settings.update({
            "allow_error_traceback": 1,  # Aktifkan error traceback
            "enable_telemetry": 0        # Nonaktifkan telemetry
        })
        system_settings.save()
        frappe.db.commit()

        frappe.msgprint("System Settings berhasil diupdate setelah install.")

    except Exception as e:
        frappe.log_error(f"Gagal mengupdate System Settings: {str(e)}", "After Install Hook Error")
        frappe.throw("Terjadi kesalahan saat mengupdate System Settings. Silakan cek log untuk detailnya.")

def after_install():
    """
    Fungsi utama yang dijalankan setelah aplikasi diinstall.
    """
    print("🟡 Installed, Setting Up Apps...")

    set_accounts_settings()  # Panggil fungsi untuk mengatur Accounts Settings
    print("... ✅ Account Settings Installed")
    # set_other_settings()     # Panggil fungsi untuk mengatur settings lainnya

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