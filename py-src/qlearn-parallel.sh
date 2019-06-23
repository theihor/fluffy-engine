#./venv/bin/python q.py 250 260 &
#./venv/bin/python q.py 261 270 &
#./venv/bin/python q.py 271 280 &
#./venv/bin/python q.py 281 290 &
#./venv/bin/python q.py 291 300 &
#./venv/bin/python q.py 295 300 
./venv/bin/python q.py 1 20 &
./venv/bin/python q.py 21 35 &
./venv/bin/python q.py 36 50 &
./venv/bin/python q.py 51 63 &
./venv/bin/python q.py 64 80 &
./venv/bin/python q.py 81 95 

wait
echo "All tasks complete!"
