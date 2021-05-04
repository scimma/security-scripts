
all: init

modify:
	rdk modify MyRule --tags '[{"Key" : "Criticality", "Value" : "Investigation" }]'

init:
	if -z "$AWS_PROFILE" ; then echo AWS_PROFILE undefined && false; else echo $AWS_PROFILE

deploy:
	rdk deploy -a

