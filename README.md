# Datenbank für Abschlussarbeiten

## Installation (für Ubuntu 16.04.2 LTS)

1. Per ssh auf Zielserver einloggen
2. Verzeichnis `/var/www` anlegen (wenn nicht vorhanden)
3. in `/var/www` git-Projekt klonen und ggf. in `thesispool/` umbenennen
4. Secret settings nach `/var/www/thesispool/thesispool/settings_secret.py` kopieren (für die Installation notwendig!)
5. Neuen `SECRET_KEY` generieren und in der `settings_secret.py` hinterlegen
6. install.sh ausführen

## ToDo / Zu beachten

- Domäne `thesis.informatik.hs-mannheim.de` registrieren (macht Herr Kühnau)
- richtiges SSL-Zertifikat generieren (am besten denselben Namen wie für das self-signed verwenden) und dann nach `/etc/ssl/<private|certs>/` kopieren (macht Herr Kühnau)
- wenn sich die Domäne ändert, muss sie in die Liste `ALLOWED_HOSTS` in `settings.py` eingetragen werden (`thesis.informatik.hs-mannheim.de` ist schon hinterlegt)