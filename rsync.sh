#/bin/bash
for host in tsunset west teast tsunrise; do
	rsync -aPv ../ietf-123-pcpu $host
done



