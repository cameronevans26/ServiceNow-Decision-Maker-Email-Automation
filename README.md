# ServiceNow Decision Maker Email Automation

This project automates the process of querying ServiceNow for decision-maker emails associated with a server CI and sending them a custom email notification. It's designed for use in enterprise environments, including integration with Ansible Tower/AWX.

---

## ✨ Features

✅ Query ServiceNow CMDB for server details  
✅ Retrieve decision-maker emails using ServiceNow API  
✅ Send templated email notifications via SMTP  
✅ Supports multiple server CIs in one run  
✅ Integrates with Ansible for automated batch execution

---

## 🔧 Prerequisites

- Python 3.6+  
- Ansible 2.9+  
- ServiceNow instance with CMDB configured  
- SMTP server available for sending emails

---

## 📂 Repository Structure

`decision_maker_email.py` # Python script for querying ServiceNow and sending emails
`decision_maker_email.yml` # Ansible playbook to run the script for multiple servers
`vault.yml` # Encrypted vault file with ServiceNow credentials (not in repo)

## 📝 Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone https://github.com/yourusername/servicenow-email-automation.git
cd servicenow-email-automation
```

### 2️⃣ Configure ServiceNow and SMTP
In decision_maker_email.py, update the following placeholders with your environment:

`SNOW_INSTANCE = "https://yourcompany.service-now.com"`
`SMTP_SERVER = "smtp.yourcompany.com"`
`SMTP_USERNAME = "donotreply@yourcompany.com"`

### 3️⃣ Set Up Ansible Vault
Create a vault.yml file to securely store your ServiceNow credentials:

```yaml
snow_username: "your_snow_username"
snow_password: "your_snow_password"
```
Encrypt it:

```bash
ansible-vault encrypt vars/vault.yml
```
>Tip: Always add `vault.yml` to your `.gitignore` to prevent accidentally sharing secrets.

### Running the Script Manually
You can run the Python script directly for a single server:

```bash
python decision_maker_email.py \
    -n "your_snow_username" \
    -k "your_snow_password" \
    --server "server_ci_name" \
    --message "This is a test notification." \
    --cc "cc1@example.com,cc2@example.com"
```

### Example Inventory
This playbook runs on localhost, so no external inventory is needed.

### Running the Playbook
```bash
ansible-playbook -i localhost, playbook.yml --ask-vault-pass \
  -e "server_cis=server1,server2" \
  -e "email_content='This is a test notification.'" \
  -e "cc_emails=cc1@example.com,cc2@example.com"
```

Example Output
`Email sent to: decisionmaker1@example.com, decisionmaker2@example.com`

If no decision makers are found, the script prints:
`No decision makers found for 'server_ci_name'.`

### Security Notes
1. This project is intended as a template. Always adapt it to your environment.
2. Do not commit vault.yml or any sensitive credentials to version control.
