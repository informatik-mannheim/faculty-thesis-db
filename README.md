# Datenbank für Abschlussarbeiten

## Installation (für Ubuntu 22.04 LTS)
## aktualisierte Version für django4

1. Per ssh auf Zielserver einloggen
2. Verzeichnis `/var/www` anlegen (wenn nicht vorhanden)
3. in `/var/www` git-Projekt klonen und ggf. in `thesispool/` umbenennen
4. Neuen `SECRET_KEY` generieren und in der `settings.py` unter SECRET_KEY hinterlegen
5. Datenbank für Studenten in `settings.py` eintragen
6. install.sh ausführen

## ToDo / Zu beachten

- Domäne `thesis.informatik.hs-mannheim.de` registrieren (macht Herr Kühnau)
- richtiges SSL-Zertifikat generieren (am besten denselben Namen wie für das self-signed verwenden) und dann nach `/etc/ssl/<private|certs>/` kopieren (macht Herr Kühnau)
- wenn sich die Domäne ändert, muss sie in die Liste `ALLOWED_HOSTS` in `settings.py` eingetragen werden (`thesis.informatik.hs-mannheim.de` ist schon hinterlegt)
