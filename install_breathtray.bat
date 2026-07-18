@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
:: ============================================================
:: BreathTray - installateur
:: Cree C:\BreathTray, installe les dependances Python,
:: lance l'app et l'ajoute au demarrage de Windows.
:: A executer en tant qu'ADMINISTRATEUR.
:: ============================================================

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Ce script doit etre execute en tant qu administrateur.
    echo Clic droit sur le fichier .bat -^> "Executer en tant qu administrateur"
    pause
    exit /b 1
)

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n est pas installe ou pas dans le PATH.
    echo Installez Python depuis https://www.python.org/downloads/ ^(cochez "Add to PATH"^) puis relancez ce script.
    pause
    exit /b 1
)

set "APPDIR=C:\BreathTray"
if not exist "%APPDIR%" mkdir "%APPDIR%"

echo Ecriture du script Python...
set "B64="
set "B64=!B64!IyAtKi0gY29kaW5nOiB1dGYtOCAtKi0KIiIiCkJyZWF0aFRyYXkgLSBHdWlkZSBkZSByZXNwaXJhdGlvbiBkYW5zIGxhIGJhcnJlIGRlcyB0YWNoZXMgV2luZG93cy4KQWZmaWNoZSB1bmUgaWNvbmUgYW5pbWVlICsgdG9vbHRpcCBlbW9qaSBxdWkgc3VpdCB1biBwcm90b2NvbGUgZGUgcmVzcGlyYXRpb24KKGluc3BpcmF0aW9uIC8gcmV0ZW50aW9uIC8gZXhwaXJhdGlvbiAvIHJldGVudGlvbikuCiIiIgoKaW1wb3J0IHRocmVhZGluZwppbXBvcnQgdGltZQppbXBvcnQgc3lzCgp0cnk6CiAgICBpbXBvcnQgcHlzdHJheQogICAg"
set "B64=!B64!ZnJvbSBQSUwgaW1wb3J0IEltYWdlLCBJbWFnZURyYXcKZXhjZXB0IEltcG9ydEVycm9yOgogICAgcHJpbnQoIk1vZHVsZXMgbWFucXVhbnRzLiBMYW5jZXo6IHB5dGhvbiAtbSBwaXAgaW5zdGFsbCBweXN0cmF5IHBpbGxvdyIpCiAgICBzeXMuZXhpdCgxKQoKUFJPVE9DT0xTID0gewogICAgIkJveCBCcmVhdGhpbmcgKDQtNC00LTQpIjogKDQsIDQsIDQsIDQpLAogICAgIjQtNy04IChyZWxheGF0aW9uKSI6ICg0LCA3LCA4LCAwKSwKICAgICJDb2hlcmVuY2UgKDUtMC01LTApIjogKDUsIDAsIDUsIDApLAogICAgIkJveCBsZW50"
set "B64=!B64!ICg1LTUtNS01KSI6ICg1LCA1LCA1LCA1KSwKfQoKUEhBU0VTID0gWyJJbnNwaXJlIiwgIlJldGllbnMiLCAiRXhwaXJlIiwgIlJldGllbnMiXQpFTU9KSVMgPSB7Ikluc3BpcmUiOiAiXFUwMDAxRjdFMlx1MkIwNiIsICJSZXRpZW5zIjogIlx1MjcwQiIsCiAgICAgICAgICAiRXhwaXJlIjogIlxVMDAwMUY1MzVcdTJCMDciLCAiUmV0aWVuc19iYXMiOiAiXHUyM0Y4In0KQ09MT1JTID0geyJJbnNwaXJlIjogKDQ2LCAyMDQsIDExMyksICJSZXRpZW5zIjogKDI0MSwgMTk2LCAxNSksCiAgICAgICAgICAiRXhwaXJlIjogKDUyLCAx"
set "B64=!B64!NTIsIDIxOSksICJSZXRpZW5zX2JhcyI6ICgxNDksIDE2NSwgMTY2KX0KCnN0YXRlID0gewogICAgInByb3RvY29sIjogIkJveCBCcmVhdGhpbmcgKDQtNC00LTQpIiwKICAgICJydW5uaW5nIjogVHJ1ZSwKICAgICJwYXVzZWQiOiBGYWxzZSwKfQoKCmRlZiBtYWtlX2ljb25faW1hZ2UocGhhc2VfbGFiZWwsIHByb2dyZXNzLCBjb2xvcik6CiAgICBzaXplID0gNjQKICAgIGltZyA9IEltYWdlLm5ldygiUkdCQSIsIChzaXplLCBzaXplKSwgKDAsIDAsIDAsIDApKQogICAgZCA9IEltYWdlRHJhdy5EcmF3KGltZykKICAgIG1pbl9y"
set "B64=!B64!LCBtYXhfciA9IDE0LCAyOAogICAgaWYgcGhhc2VfbGFiZWwgPT0gIkluc3BpcmUiOgogICAgICAgIHIgPSBtaW5fciArIChtYXhfciAtIG1pbl9yKSAqIHByb2dyZXNzCiAgICBlbGlmIHBoYXNlX2xhYmVsID09ICJFeHBpcmUiOgogICAgICAgIHIgPSBtYXhfciAtIChtYXhfciAtIG1pbl9yKSAqIHByb2dyZXNzCiAgICBlbHNlOgogICAgICAgIHIgPSBtYXhfcgogICAgY3ggPSBjeSA9IHNpemUgLyAyCiAgICBkLmVsbGlwc2UoW2N4IC0gciwgY3kgLSByLCBjeCArIHIsIGN5ICsgcl0sIGZpbGw9Y29sb3IgKyAoMjU1LCkpCiAg"
set "B64=!B64!ICBkLmVsbGlwc2UoW2N4IC0gciwgY3kgLSByLCBjeCArIHIsIGN5ICsgcl0sIG91dGxpbmU9KDI1NSwgMjU1LCAyNTUsIDIyMCksIHdpZHRoPTMpCiAgICByZXR1cm4gaW1nCgoKZGVmIHBoYXNlX2tleShwaGFzZV9sYWJlbCwgaW5kZXgpOgogICAgcmV0dXJuICJSZXRpZW5zIiBpZiBpbmRleCA9PSAxIGVsc2UgKCJSZXRpZW5zX2JhcyIgaWYgaW5kZXggPT0gMyBlbHNlIHBoYXNlX2xhYmVsKQoKCmRlZiBicmVhdGhpbmdfbG9vcChpY29uKToKICAgIHdoaWxlIHN0YXRlWyJydW5uaW5nIl06CiAgICAgICAgaWYgc3RhdGVbInBh"
set "B64=!B64!dXNlZCJdOgogICAgICAgICAgICBpY29uLnRpdGxlID0gIkJyZWF0aFRyYXkgLSBFbiBwYXVzZSAoY2xpYyBkcm9pdCBwb3VyIHJlcHJlbmRyZSkiCiAgICAgICAgICAgIHRpbWUuc2xlZXAoMC4zKQogICAgICAgICAgICBjb250aW51ZQoKICAgICAgICBkdXJhdGlvbnMgPSBQUk9UT0NPTFNbc3RhdGVbInByb3RvY29sIl1dCiAgICAgICAgZm9yIGlkeCwgKGxhYmVsLCBzZWNvbmRzKSBpbiBlbnVtZXJhdGUoemlwKFBIQVNFUywgZHVyYXRpb25zKSk6CiAgICAgICAgICAgIGlmIHNlY29uZHMgPD0gMDoKICAgICAgICAgICAgICAg"
set "B64=!B64!IGNvbnRpbnVlCiAgICAgICAgICAgIGtleSA9IHBoYXNlX2tleShsYWJlbCwgaWR4KQogICAgICAgICAgICBjb2xvciA9IENPTE9SU1trZXldCiAgICAgICAgICAgIGVtb2ppID0gRU1PSklTW2tleV0KICAgICAgICAgICAgc3RlcHMgPSBtYXgoaW50KHNlY29uZHMgKiA0KSwgMSkKICAgICAgICAgICAgZm9yIHMgaW4gcmFuZ2Uoc3RlcHMpOgogICAgICAgICAgICAgICAgaWYgbm90IHN0YXRlWyJydW5uaW5nIl06CiAgICAgICAgICAgICAgICAgICAgcmV0dXJuCiAgICAgICAgICAgICAgICB3aGlsZSBzdGF0ZVsicGF1c2VkIl06"
set "B64=!B64!CiAgICAgICAgICAgICAgICAgICAgdGltZS5zbGVlcCgwLjIpCiAgICAgICAgICAgICAgICBwcm9ncmVzcyA9IHMgLyBzdGVwcwogICAgICAgICAgICAgICAgcmVtYWluaW5nID0gcm91bmQoc2Vjb25kcyAtIChzIC8gc3RlcHMpICogc2Vjb25kcykKICAgICAgICAgICAgICAgIGljb24uaWNvbiA9IG1ha2VfaWNvbl9pbWFnZShsYWJlbCwgcHJvZ3Jlc3MsIGNvbG9yKQogICAgICAgICAgICAgICAgaWNvbi50aXRsZSA9ICJ7MH0gezF9IC0gezJ9cyAgW3szfV0iLmZvcm1hdCgKICAgICAgICAgICAgICAgICAgICBlbW9qaSwgbGFi"
set "B64=!B64!ZWwsIHJlbWFpbmluZywgc3RhdGVbInByb3RvY29sIl0pCiAgICAgICAgICAgICAgICB0aW1lLnNsZWVwKDAuMjUpCgoKZGVmIGJ1aWxkX3Byb3RvY29sX21lbnUoKToKICAgIGl0ZW1zID0gW10KICAgIGZvciBuYW1lIGluIFBST1RPQ09MUzoKICAgICAgICBkZWYgbWFrZV9oYW5kbGVyKG4pOgogICAgICAgICAgICBkZWYgaGFuZGxlcihpY29uLCBpdGVtKToKICAgICAgICAgICAgICAgIHN0YXRlWyJwcm90b2NvbCJdID0gbgogICAgICAgICAgICByZXR1cm4gaGFuZGxlcgogICAgICAgIGl0ZW1zLmFwcGVuZCgKICAgICAgICAg"
set "B64=!B64!ICAgcHlzdHJheS5NZW51SXRlbSgKICAgICAgICAgICAgICAgIG5hbWUsIG1ha2VfaGFuZGxlcihuYW1lKSwKICAgICAgICAgICAgICAgIGNoZWNrZWQ9bGFtYmRhIGl0ZW0sIG49bmFtZTogc3RhdGVbInByb3RvY29sIl0gPT0gbiwKICAgICAgICAgICAgICAgIHJhZGlvPVRydWUsCiAgICAgICAgICAgICkKICAgICAgICApCiAgICByZXR1cm4gaXRlbXMKCgpkZWYgdG9nZ2xlX3BhdXNlKGljb24sIGl0ZW0pOgogICAgc3RhdGVbInBhdXNlZCJdID0gbm90IHN0YXRlWyJwYXVzZWQiXQoKCmRlZiBxdWl0X2FwcChpY29uLCBpdGVt"
set "B64=!B64!KToKICAgIHN0YXRlWyJydW5uaW5nIl0gPSBGYWxzZQogICAgaWNvbi5zdG9wKCkKCgpkZWYgbWFpbigpOgogICAgbWVudSA9IHB5c3RyYXkuTWVudSgKICAgICAgICBweXN0cmF5Lk1lbnVJdGVtKCJQYXVzZSAvIFJlcHJlbmRyZSIsIHRvZ2dsZV9wYXVzZSksCiAgICAgICAgcHlzdHJheS5NZW51LlNFUEFSQVRPUiwKICAgICAgICBweXN0cmF5Lk1lbnVJdGVtKCJQcm90b2NvbGUiLCBweXN0cmF5Lk1lbnUoKmJ1aWxkX3Byb3RvY29sX21lbnUoKSkpLAogICAgICAgIHB5c3RyYXkuTWVudS5TRVBBUkFUT1IsCiAgICAgICAgcHlz"
set "B64=!B64!dHJheS5NZW51SXRlbSgiUXVpdHRlciIsIHF1aXRfYXBwKSwKICAgICkKICAgIGljb24gPSBweXN0cmF5Lkljb24oCiAgICAgICAgIkJyZWF0aFRyYXkiLAogICAgICAgIG1ha2VfaWNvbl9pbWFnZSgiSW5zcGlyZSIsIDAuMCwgQ09MT1JTWyJJbnNwaXJlIl0pLAogICAgICAgICJCcmVhdGhUcmF5IiwKICAgICAgICBtZW51LAogICAgKQogICAgdGhyZWFkaW5nLlRocmVhZCh0YXJnZXQ9YnJlYXRoaW5nX2xvb3AsIGFyZ3M9KGljb24sKSwgZGFlbW9uPVRydWUpLnN0YXJ0KCkKICAgIGljb24ucnVuKCkKCgppZiBfX25hbWVfXyA9"
set "B64=!B64!PSAiX19tYWluX18iOgogICAgbWFpbigpCg=="

powershell -NoProfile -ExecutionPolicy Bypass -Command "[IO.File]::WriteAllBytes('%APPDIR%\breath_tray.py', [Convert]::FromBase64String($env:B64))"
if not exist "%APPDIR%\breath_tray.py" (
    echo [ERREUR] Echec de l ecriture du script Python.
    pause
    exit /b 1
)

echo Installation des dependances Python (pystray, pillow)...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install pystray pillow
if %errorlevel% neq 0 (
    echo [ERREUR] Echec de l installation des dependances pip.
    pause
    exit /b 1
)

echo Creation du raccourci de demarrage automatique...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([Environment]::GetFolderPath('Startup') + '\BreathTray.lnk'); $s.TargetPath = (Get-Command pythonw.exe).Source; $s.Arguments = '%APPDIR%\breath_tray.py'; $s.WorkingDirectory = '%APPDIR%'; $s.WindowStyle = 7; $s.Description = 'BreathTray - guide de respiration'; $s.Save()"

echo Lancement de BreathTray...
start "" pythonw.exe "%APPDIR%\breath_tray.py"

echo.
echo ============================================================
echo  Installation terminee.
echo  BreathTray tourne dans la zone de notification (pres de l horloge).
echo  Clic droit sur l icone pour changer de protocole, pause, quitter.
echo  L app se relancera automatiquement a chaque demarrage de Windows.
echo ============================================================
pause
endlocal
