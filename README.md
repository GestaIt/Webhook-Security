# Webhook Security
 A Discord webhook proxy that prevents spamming.

# Initialization
Download the files as a zip, and extract the main folder to your desktop, then make a JSON file in the root directory and name it 'config.json'.

Inside 'config.json', make sure you have the following.

```json
{
  "discord-token": "Discord bot token",
  "prefix": "Prefix",
  "guild-id": "Root Guild ID",
  "owner-role-id": "Owner role, used for role snowflakes",
  "moderator-role-id": "Moderator role",
  "whitelist-role-id": "Whitelisted role"
}
```

# Licensed under 'Unlicense'