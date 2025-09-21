@echo off
:loop
python bot.py
echo Bot crashed or exited. Restarting in 5 seconds...
timeout /t 5
goto loop
