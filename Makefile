PLUGIN_NAME=        configsync
PLUGIN_VERSION=     0.4.34
PLUGIN_COMMENT=     Synchronize system configuration .xml files to various cloud-storage providers
PLUGIN_MAINTAINER=  contact@threatpatrols.com
PLUGIN_WWW=         https://documentation.threatpatrols.com/opnsense/plugins/configsync/

# NB: PLUGIN_DEPENDS is generated at build-time based on the Python version on the then-current OPNsense version
PLUGIN_DEPENDS=

PLUGIN_PREFIX=		os-
PLUGIN_SUFFIX=
PLUGIN_DEVEL=       no

_VERSION_UPDATE!=   echo "__version__ = \"${PLUGIN_VERSION}\"" > src/opnsense/scripts/ThreatPatrols/ConfigSync/configsync/__version__.py

.include "../../Mk/plugins.mk"
