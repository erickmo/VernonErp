import frappe
from frappe.utils import getdate, add_years

def create_missing_fiscal_years():
	"""
	Scheduled job to automatically create missing fiscal years for all companies.
	Fiscal year runs from January 1 to December 31.
	"""
	# Ambil semua data fiscal years
	fiscal_years = frappe.get_all("Fiscal Year", fields=["name", "year_start_date", "year_end_date"])

	# Ambil semua data company
	companies = frappe.get_all("Company", fields=["name"])

	# ambil fiscal year paling awal
	earliest_fiscal_year = min(fiscal_years, key=lambda x: x.year_start_date)

	# loop dari earliest fiscal year sampai tahun hari ini
	current_year = getdate().year
	start_year = getdate(earliest_fiscal_year.year_start_date).year

	for year in range(start_year, current_year + 2):
		# kalau belum ada fiscal_year.year == year, maka buat fiscal year baru
		if not any(fy.year_start_date.year == year for fy in fiscal_years):
			# buat fiscal year baru
			fiscal_year = frappe.new_doc("Fiscal Year")
			fiscal_year.year = year
			fiscal_year.year_start_date = "{}-01-01".format(year)
			fiscal_year.year_end_date = "{}-12-31".format(year)

			# untuk setiap company di companies, masukkan di fiscal_year.companies kalau belum ada
			for company in companies:
				if not any(c.company == company.name for c in fiscal_year.companies):
					fiscal_year.append("companies", {
						"company": company.name
					})
			
			fiscal_year.insert()
			frappe.db.commit()


			