import frappe


def before_request_test():
	print("🔥 BEFORE REQUEST TRIGGERED 🔥")
	frappe.logger().error("🔥 BEFORE REQUEST TRIGGERED 🔥")
