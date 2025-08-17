pg_dump -h localhost -U postgres -W -d ticket_management_system -F c -f ticket_management_system.backup

pg_restore -h localhost -U postgres -W -d new_ticket_management_system ticket_management_system.backup
