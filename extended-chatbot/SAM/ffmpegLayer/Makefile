build-ffmpegLayer:
	mkdir -p "$(ARTIFACTS_DIR)/tmp"
	mkdir -p "$(ARTIFACTS_DIR)/bin"
	curl -sS https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz > "$(ARTIFACTS_DIR)/tmp/ffmpeg.tar.xz"
	tar xf "$(ARTIFACTS_DIR)/tmp/ffmpeg.tar.xz" -C "$(ARTIFACTS_DIR)/tmp"
	cp $(ARTIFACTS_DIR)/tmp/ffmpeg-*-static/ffmpeg $(ARTIFACTS_DIR)/tmp/ffmpeg-*-static/ffprobe "$(ARTIFACTS_DIR)/bin"
	rm -r "$(ARTIFACTS_DIR)/tmp"
