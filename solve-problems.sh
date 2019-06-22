num_procs=4
num_jobs="\j"

for desc in ./desc/prob-*.desc; do
    dir=${desc%/*}
    base=${desc##*/}
    sol=${dir}/${base%.desc}.sol
    while (( ${num_jobs@P} >= num_procs )); do
    	wait -n
    done
    ./py-src/venv/bin/python ./py-src/main.py "$desc" "$sol" &
done

wait
echo "All tasks complete!"
