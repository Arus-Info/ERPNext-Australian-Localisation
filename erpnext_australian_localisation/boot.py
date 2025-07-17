import frappe

def set_bootinfo(bootinfo):
    au_localisation_settings = frappe.get_cached_doc("AU Localisation Settings").as_dict()
    bootinfo["au_localisation_settings"] = au_localisation_settings