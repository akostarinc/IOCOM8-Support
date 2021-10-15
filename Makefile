
all:
	@echo "Usage: make [target] -- where target is one of: 'git' 'doc' 'clean 'sum' "

# Genetrate checksum (recommend Whole project clean before)

sum:
	./gensum.sh

# Whole project clean

clean:
	make clean -C qcan_espnow
	make clean -C qcan_can
	make clean -C ui_espnow
	make clean -C mon_espnow/v000

# Auto Checkin

ifeq ("$(AUTOCHECK)","")
AUTOCHECK=autocheck
endif

git:
	git add .
	git commit -m "$(AUTOCHECK)"
	git push

# Documentation

doc:
	(cd wclock; doxygen; cd ..)



