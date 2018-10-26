for i in {1..81}; do 
 temp=`echo "scale=0; (($i * 3.2963) + 178)/1" | bc -l`
 echo '{'
 echo '    "fanSpeed": 9,'
 echo '    "targetTemp": '${temp}','
 echo '    "sectionTime": 9,'
 echo '},'
done