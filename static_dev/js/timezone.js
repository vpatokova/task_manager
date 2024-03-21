const timezone = Intl
    .DateTimeFormat()
    .resolvedOptions().timeZone

document.cookie = "client_timezone=" + timezone