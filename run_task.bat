cd aria2_x64
start aria2c.exe --conf-path=aria2.conf
cd ..
python -m pip install -r requirements.txt
python task.py -t
pause