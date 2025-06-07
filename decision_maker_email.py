#!/usr/bin/env python3

"""
ServiceNow Decision Maker Email Script

This script queries a ServiceNow instance for decision-maker emails tied to a given server name
and sends them an email with a custom message.

NOTE:
- You must provide ServiceNow credentials and SMTP configuration.
- Adjust the SNOW_INSTANCE and SMTP_* variables before use.
- This script is intended as a **template**—modify it as needed for your environment.
"""

import sys
import requests
import smtplib
from argparse import ArgumentParser
from email.mime.text import MIMEText

# Global variables for ServiceNow and SMTP configurations.
SNOW_INSTANCE = "https://yourcompany.service-now.com"  # Replace with your ServiceNow instance URL

SMTP_SERVER = "smtp.yourcompany.com"  # Replace with your SMTP server
SMTP_PORT = 25  # Default SMTP port; adjust if needed
SMTP_USERNAME = "donotreply@yourcompany.com"  # Replace with your sender email address

def parse_options(args):
    """Parse command-line arguments."""
    parser = ArgumentParser(
        description='Send an email to decision makers for a given server CI in ServiceNow.'
    )
    parser.add_argument("-n", "--user", type=str, required=True,
                        help="ServiceNow Username")
    parser.add_argument("-k", "--pwd", type=str, required=True,
                        help="ServiceNow Password")
    parser.add_argument("--server", type=str, required=True,
                        help="Server CI Name to query")
    parser.add_argument("--message", type=str, required=True,
                        help="Custom email message content")
    parser.add_argument("--cc", type=str, default="",
                        help="Comma-separated list of CC emails")

    return parser.parse_args(args)

def get_server_sys_id(server_name, snow_user, snow_pwd):
    """Fetches the sys_id of the given server name."""
    url = f"{SNOW_INSTANCE}/api/now/table/cmdb_ci_server"
    params = {
        "sysparm_query": f"name={server_name}",
        "sysparm_display_value": "true",
        "sysparm_exclude_reference_link": "true",
        "sysparm_fields": "sys_id"
    }
    response = requests.get(url, auth=(snow_user, snow_pwd), params=params)
    response.raise_for_status()
    result = response.json().get("result", [])
    return result[0]["sys_id"] if result else None

def get_decision_makers(server_sys_id, snow_user, snow_pwd):
    """Fetches decision-maker emails for a given server sys_id."""
    url = f"{SNOW_INSTANCE}/api/now/table/u_ci_decision_maker_members"
    params = {
        "sysparm_query": f"ci_sys_id={server_sys_id}",
        "sysparm_display_value": "true",
        "sysparm_exclude_reference_link": "true",
        "sysparm_fields": "mem_user.email"
    }
    response = requests.get(url, auth=(snow_user, snow_pwd), params=params)
    response.raise_for_status()
    return [entry["mem_user.email"]
            for entry in response.json().get("result", [])
            if "mem_user.email" in entry]

def send_email(to_emails, cc_emails, subject, body):
    """Sends an email to the decision makers and optional CC list."""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USERNAME
    msg["To"] = ", ".join(to_emails)
    if cc_emails:
        msg["CC"] = ", ".join(cc_emails)

    recipients = to_emails + cc_emails

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.sendmail(SMTP_USERNAME, recipients, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

def main():
    """Main execution flow."""
    args = parse_options(sys.argv[1:])

    snow_user = args.user
    snow_pwd = args.pwd
    server_name = args.server
    custom_message = args.message
    cc_emails = args.cc.split(",") if args.cc else []

    try:
        server_sys_id = get_server_sys_id(server_name, snow_user, snow_pwd)
        if not server_sys_id:
            print(f"Error: Server '{server_name}' not found in ServiceNow.")
            return

        decision_maker_emails = get_decision_makers(server_sys_id, snow_user, snow_pwd)
        if decision_maker_emails:
            subject = f"Action Required: {server_name} - Important Update"
            body = f"Dear Decision Makers,\n\n{custom_message}"
            send_email(decision_maker_emails, cc_emails, subject, body)
            print(f"Email sent to: {', '.join(decision_maker_emails)}")
        else:
            print(f"No decision makers found for '{server_name}'.")
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
