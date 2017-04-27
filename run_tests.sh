#!/bin/bash
echo Running tests..

results_file=results.txt

server=palvelin
# ports=( 8081 8082 8083 )
ports=( 8081 )
# concurrencies=( 1 3 10 31 100 316 1000 )
# concurrencies=( 1 10 100 1000 )
concurrencies=( 10 )
# requests=( 1000 )
requests=( 100 )

> ${results_file}

for port in "${ports[@]}"
do
  for n in "${requests[@]}"
  do
    for c in "${concurrencies[@]}"
    do
      python -m boom.boom http://${server}:${port} -n ${n} -c ${c} >> ${results_file}
      # sleep 5
    done
    # sleep 5
  done
  # sleep 10
done

# python parse_results.py ${results_file}

echo Done.