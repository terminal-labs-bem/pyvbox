APPNAME="template"
SUDOUSERNAME=$(SUDO_USER)
CONFIGURATION="default"
TYPE="python"
PYTHONVERSION="3.11"
HOSTTYPE="default"
INTERNALUSER=$(SUDO_USER)
PLATFORM=".tlcache"
PLUGIN="standard"
EXTRA="none"

help:
	@echo "usage: make [command]"

define kickoff
	@sudo bash .tmp/bem/common/preinstall.sh $(APPNAME) $(SUDOUSERNAME) $(CONFIGURATION) $(TYPE) $(PYTHONVERSION) $(HOSTTYPE) $(INTERNALUSER) $(PLATFORM) $(PLUGIN) $(EXTRA)
endef

download_bash_environment_manager:
	@if test ! -d ".tmp";then \
		sudo su -m $(SUDO_USER) -c "mkdir -p .tmp"; \
		sudo su -m $(SUDO_USER) -c "mkdir -p .tmp/prep"; \
		sudo su -m $(SUDO_USER) -c "mkdir -p .tmp/bem"; \
		sudo su -m $(SUDO_USER) -c "mkdir -p .tmp/task"; \
  		sudo su -m $(SUDO_USER) -c "cd .tmp/prep; wget -O shelf-main.zip https://github.com/terminal-labs-bem/shelf/archive/refs/heads/main.zip"; \
  		sudo su -m $(SUDO_USER) -c "cd .tmp/prep; unzip -n shelf-main.zip"; \
  		sudo su -m $(SUDO_USER) -c "cp -r .tmp/prep/shelf-main/bem/* .tmp/bem"; \
  		sudo su -m $(SUDO_USER) -c "cp -r .tmp/prep/shelf-main/task/* .tmp/task"; \
	fi

rye: HOSTTYPE="host"
rye: INTERNALUSER=$(SUDO_USER)
rye: download_bash_environment_manager
	$(call kickoff)

vm.rye: HOSTTYPE="vagrant"
vm.rye: INTERNALUSER="vagrant"
vm.rye: download_bash_environment_manager
	@if test ! -f "Vagrantfile";then \
		wget https://raw.githubusercontent.com/terminal-labs/bash-environment-manager-shelf/main/vagrantfiles/Vagrantfile; \
		chown $(SUDO_USER) Vagrantfile; \
	fi
	$(call kickoff)
