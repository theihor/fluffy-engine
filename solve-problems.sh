num_procs=8
num_jobs="\j"

for desc in ./desc/prob-*.desc; do
    dir=${desc%/*/*}
    base=${desc##*/}
    sol=${dir}/sol/${base%.desc}.sol
    while (( ${num_jobs@P} >= num_procs )); do
    	wait -n
    done
    ( ./py-src/venv/bin/python ./py-src/main.py "$desc" "$sol";\
      echo "Task $desc finished.") &
done

wait
echo "All tasks complete!"
