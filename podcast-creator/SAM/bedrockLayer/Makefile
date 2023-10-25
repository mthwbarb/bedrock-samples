build-bedrockLayer:
	mkdir -p "$(ARTIFACTS_DIR)/python"
	cp * "$(ARTIFACTS_DIR)/python"
	python3.11 -m pip install --no-build-isolation --force-reinstall /tmp/dependencies/boto3-*-py3-none-any.whl /tmp/dependencies/botocore-*-py3-none-any.whl -t "$(ARTIFACTS_DIR)/python"
	#python3.8 -m pip install urllib3==1.26.6