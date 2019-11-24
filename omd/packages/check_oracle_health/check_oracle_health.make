CHECK_ORACLE_HEALTH := check_oracle_health
CHECK_ORACLE_HEALTH_VERS := 3.0.1
CHECK_ORACLE_HEALTH_DIR := $(CHECK_ORACLE_HEALTH)-$(CHECK_ORACLE_HEALTH_VERS)

CHECK_ORACLE_HEALTH_UNPACK := $(BUILD_HELPER_DIR)/$(CHECK_ORACLE_HEALTH_DIR)-unpack
CHECK_ORACLE_HEALTH_BUILD := $(BUILD_HELPER_DIR)/$(CHECK_ORACLE_HEALTH_DIR)-build
CHECK_ORACLE_HEALTH_INSTALL := $(BUILD_HELPER_DIR)/$(CHECK_ORACLE_HEALTH_DIR)-install
CHECK_ORACLE_HEALTH_SKEL := $(BUILD_HELPER_DIR)/$(CHECK_ORACLE_HEALTH_DIR)-skel

#CHECK_ORACLE_HEALTH_INSTALL_DIR := $(INTERMEDIATE_INSTALL_BASE)/$(CHECK_ORACLE_HEALTH_DIR)
CHECK_ORACLE_HEALTH_BUILD_DIR := $(PACKAGE_BUILD_DIR)/$(CHECK_ORACLE_HEALTH_DIR)
#CHECK_ORACLE_HEALTH_WORK_DIR := $(PACKAGE_WORK_DIR)/$(CHECK_ORACLE_HEALTH_DIR)

.PHONY: $(CHECK_ORACLE_HEALTH)-clean

# Configure options for Nagios. Since we want to compile
# as non-root, we use our own user and group for compiling.
# All files will be packaged as user 'root' later anyway.
CHECK_ORACLE_HEALTH_CONFIGUREOPTS = ""

$(CHECK_ORACLE_HEALTH_BUILD): $(CHECK_ORACLE_HEALTH_UNPACK)
	for i in configure.ac aclocal.m4 configure Makefile.am Makefile.in ; do \
	  test -f $(CHECK_ORACLE_HEALTH_BUILD_DIR)/$$i && touch $(CHECK_ORACLE_HEALTH_BUILD_DIR)/$$i ; \
	done
	cd $(CHECK_ORACLE_HEALTH_BUILD_DIR) ; ./configure $(CHECK_ORACLE_HEALTH_CONFIGUREOPTS)
	$(MAKE) -C $(CHECK_ORACLE_HEALTH_BUILD_DIR)
	$(TOUCH) $@

$(CHECK_ORACLE_HEALTH_INSTALL): $(CHECK_ORACLE_HEALTH_BUILD)
	install -m 755 $(CHECK_ORACLE_HEALTH_BUILD_DIR)/plugins-scripts/check_oracle_health $(DESTDIR)$(OMD_ROOT)/lib/nagios/plugins
	$(TOUCH) $@

$(CHECK_ORACLE_HEALTH_SKEL):
	$(TOUCH) $@

$(CHECK_ORACLE_HEALTH)-clean:
	rm -rf $(CHECK_ORACLE_HEALTH_BUILD_DIR) $(BUILD_HELPER_DIR)/$(CHECK_ORACLE_HEALTH_DIR)*
