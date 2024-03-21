def normalize_email(email):
    email = email.strip().lower()
    username, domain = email.split("@")
    email = f"{username.split('+')[0]}@{domain}"
    if email.endswith("@ya.ru"):
        email = email.replace("@ya.ru", "@yandex.ru")
    if email.endswith("@gmail.com"):
        username, domain = email.split("@")
        username = username.replace(".", "")
        email = f"{username}@{domain}"
    if email.endswith("@yandex.ru"):
        username, domain = email.split("@")
        username = username.replace(".", "-")
        email = f"{username}@{domain}"
    return email
