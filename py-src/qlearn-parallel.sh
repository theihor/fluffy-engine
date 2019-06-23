./venv/bin/python q.py 1 100 ../qmaps/fresh1.pickle &
./venv/bin/python q.py 100 150 ../qmaps/fresh2.pickle &
./venv/bin/python q.py 150 210 ../qmaps/fresh3.pickle &
./venv/bin/python q.py 210 250 ../qmaps/fresh4.pickle &
./venv/bin/python q.py 260 301 ../qmaps/fresh5.pickle &
./venv/bin/python q.py 235 275 ../qmaps/fresh6.pickle 

wait
echo "All tasks complete!"
