./venv/bin/python q.py 1 130 ../qmaps/fresh.pickle &
./venv/bin/python q.py 131 180 ../qmaps/fresh.pickle &
./venv/bin/python q.py 200 270 ../qmaps/fresh.pickle &
./venv/bin/python q.py 271 300 ../qmaps/fresh.pickle &
./venv/bin/python q.py 1 200 ../qmaps/qmap5.pickle &
./venv/bin/python q.py 201 300 ../qmaps/qmap6.pickle &

wait
echo "All tasks complete!"
