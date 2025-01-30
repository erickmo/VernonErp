import frappe
import re
from frappe.model.document import Document

class WalletTokopedia(Document):
	def before_insert(self):
		""" 
		1️⃣ Menentukan tipe_transaksi berdasarkan pola regex dari description
		2️⃣ Mengambil nomor rekening tujuan (withdrawal_to) jika deskripsi adalah withdrawal
		"""

		# 1️⃣ Menentukan tipe_transaksi berdasarkan pola di description
		result = self.get_tipe_transaksi(self.description)
		self.tipe_transaksi = result["tipe_transaksi"]
		self.no_pesanan = result["no_pesanan"]

		# 2️⃣ Jika tipe transaksi adalah withdrawal, ambil rekening tujuan
		if self.tipe_transaksi == "withdrawal":
			self.withdrawal_to = self.extract_withdrawal_account(self.description)
		
	def get_tipe_transaksi(self, description):
		# Mapping pola regex ke tipe transaksi yang sesuai
		patterns = {
			r"Pemotongan Biaya Layanan Bebas Ongkir Power Shop - INV/([\w/\d]+)": "biaya bebas ongkir",
			r"Pemotongan Biaya Layanan Power Shop - INV/([\w/\d]+)": "biaya admin ecommerce",
			r"Transaksi Penjualan Berhasil - INV/([\w/\d]+)": "payment",
			r"Withdrawal \(PT\. BCA .*? - (\d+) - .*?\)": "withdrawal",
			r"Pemotongan Selisih Ongkir via SiCepat .*? INV/([\w/\d]+)": "biaya ongkir",
			r"Penggunaan Saldo Tokopedia untuk pembelian dari Tokopedia Ads": "biaya ads",
			r"Pemotongan Saldo untuk Kupon Toko .*? untuk Invoice (INV/[\w/\d]+)": "biaya marketing",
			r"Dipotong karena Solusi dari Resolusi - (INV/[\w/\d]+)": "biaya kalah komplain"
		}

		# Mencocokkan pola dengan deskripsi transaksi
		for pattern, tipe in patterns.items():
			match = re.search(pattern, description)
			if match:
				if tipe == "withdrawal":
					no_pesanan = None
				else:
					no_pesanan = match.group(1) if len(match.groups()) > 0 else None

				return {"tipe_transaksi": tipe, "no_pesanan": no_pesanan}

		# Default jika tidak ada yang cocok
		return {"tipe_transaksi": "lainnya", "no_pesanan": None}

	def extract_withdrawal_account(self, description):
		"""Mengambil nomor rekening tujuan dari deskripsi withdrawal"""
		match = re.search(r"Withdrawal \(PT\. BCA .*? - (\d+) - .*?\)", description)
		return match.group(1) if match else None