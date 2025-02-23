# Copyright (c) 2025, VernonCorp and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from erpnext.accounts.utils import get_balance_on

class AccountBalance(Document):
	def on_save(self):
		# kalau gl_balance_fetch_at < modified atau gl_balance_fetch_at = None, set status = None
		if self.gl_balance_fetch_at < self.modified or self.gl_balance_fetch_at == None:
			self.status = None
			self.gl_balance = None		