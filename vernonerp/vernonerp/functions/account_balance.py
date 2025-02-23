import frappe
import json
from erpnext.accounts.utils import get_balance_on

# Create whitelist function 
@frappe.whitelist()
def execute(*args,**kwargs):

	# set doc_name dari doc_json ambil 'name'
	doc_data = json.loads(kwargs['doc'])
	doc_name = doc_data['name']

	# if no docname, return
	if not doc_name:
		return

	# Get Document
	doc = frappe.get_doc("Account Balance", doc_name)

	# ambil account_balance_name
	balance = get_balance_on(doc.account, date=doc.balance_date)
	
	# get balance
	doc.gl_balance = balance
	doc.gl_balance_fetch_at = frappe.utils.now()
	
	# Set the status based on the fetched balance
	if doc.gl_balance == doc.balance:
		doc.status = "balance"
	else:
		doc.status = "not balance"
	
	# Save the document to update the fields
	doc.save()

	# Info done
	frappe.msgprint(f"Account Balance Updated. Status: {doc.status}")